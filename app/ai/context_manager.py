"""
Context Manager
Orchestrates the full AI workflow: context retrieval → prompt building → provider call.
"""
import time
import logging

from app.ai.provider_factory import get_provider, get_backup_provider
from app.ai.prompt_builder import PromptBuilder
from app.services.knowledge_service import KnowledgeService
from app.services.chat_service import ChatService
from app.services.analytics_service import AnalyticsService

logger = logging.getLogger(__name__)


def _get_student_assignments(user_id):
    """Fetch upcoming/recent assignments across a student's enrolled subjects,
    for injection into the AI system prompt. Best-effort — never raises."""
    try:
        from app.services.allocation_service import AllocationService
        from app.models.assignment import Assignment
        subjects = AllocationService.get_enrolled_subjects(user_id)
        subject_ids = [s.id for s in subjects]
        if not subject_ids:
            return []
        return (Assignment.query.filter(Assignment.subject_id.in_(subject_ids))
                .order_by(Assignment.due_date.asc()).limit(20).all())
    except Exception:
        return []


class ContextManager:

    @staticmethod
    def process_message(user, session_id, user_message, subject_id=None,
                        ip_address=None, user_agent=None):
        """Full AI pipeline: retrieve context → build prompt → call AI → save → return response.
        Returns (response_text, metadata_dict) or raises RuntimeError.
        """
        # 1. Retrieve knowledge context for the student
        knowledge_context, resource_files = KnowledgeService.get_context_for_student(
            department_id=user.department_id,
            program_id=user.program_id,
            batch_id=user.batch_id,
            semester_id=user.semester_id,
            subject_id=subject_id,
        )
        assignments = _get_student_assignments(user.id)

        # 2. Get AI provider default prompt
        provider_instance = get_provider()
        from app.models.ai_settings import AIProvider
        primary = AIProvider.query.filter_by(is_primary=True, is_active=True).first()
        custom_prompt = primary.default_prompt if primary else None

        # 3. Build system prompt
        system_prompt = PromptBuilder.build_system_prompt(
            user=user,
            knowledge_context=knowledge_context,
            resource_files=resource_files,
            custom_prompt=custom_prompt,
            assignments=assignments,
        )

        # 4. Save user message
        ChatService.add_message(
            session_id=session_id,
            role='user',
            content=user_message,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # 5. Get conversation history
        history = ChatService.get_conversation_history(session_id, limit=20)

        # 6. Call AI provider with failover
        start_time = time.time()
        try:
            response_text, metadata = provider_instance.generate(history, system_prompt)
        except Exception as e:
            logger.warning(f'Primary provider failed: {e}. Trying backup.')
            backup = get_backup_provider()
            if backup:
                response_text, metadata = backup.generate(history, system_prompt)
            else:
                raise RuntimeError(f'AI provider error: {e}')

        response_time_ms = int((time.time() - start_time) * 1000)

        # 7. Save assistant response
        ChatService.add_message(
            session_id=session_id,
            role='assistant',
            content=response_text,
            provider_used=metadata.get('provider'),
            model_used=metadata.get('model'),
            response_time_ms=response_time_ms,
            tokens_used=metadata.get('tokens'),
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # 8. Track analytics
        AnalyticsService.track(
            event_type='chat',
            user_id=user.id,
            department_id=user.department_id,
            subject_id=subject_id,
            event_data={'response_time_ms': response_time_ms},
            ip=ip_address,
            ua=user_agent,
        )
        AnalyticsService.track_question(user_message, user.department_id, subject_id)

        metadata['response_time_ms'] = response_time_ms
        metadata['resource_files'] = resource_files
        return response_text, metadata

    @staticmethod
    def process_message_stream(user, session_id, user_message, subject_id=None,
                               ip_address=None, user_agent=None):
        """Streaming version — yields chunks. Saves complete response at the end."""
        # Capture plain values upfront to avoid lazy-load issues in generator
        user_id = user.id
        dept_id = user.department_id
        prog_id = user.program_id
        batch_id = user.batch_id
        semester_id = user.semester_id

        knowledge_context, resource_files = KnowledgeService.get_context_for_student(
            department_id=dept_id,
            program_id=prog_id,
            batch_id=batch_id,
            semester_id=semester_id,
            subject_id=subject_id,
        )
        assignments = _get_student_assignments(user_id)

        provider_instance = get_provider()
        from app.models.ai_settings import AIProvider
        primary = AIProvider.query.filter_by(is_primary=True, is_active=True).first()
        custom_prompt = primary.default_prompt if primary else None
        provider_slug = primary.slug if primary else 'unknown'
        model_name = primary.model_name if primary else 'unknown'

        system_prompt = PromptBuilder.build_system_prompt(
            user=user,
            knowledge_context=knowledge_context,
            resource_files=resource_files,
            custom_prompt=custom_prompt,
            assignments=assignments,
        )

        ChatService.add_message(
            session_id=session_id,
            role='user',
            content=user_message,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        history = ChatService.get_conversation_history(session_id, limit=20)

        start_time = time.time()
        full_response = []

        try:
            for chunk in provider_instance.generate_stream(history, system_prompt):
                full_response.append(chunk)
                yield chunk
        except Exception as e:
            logger.warning(f'Streaming primary failed: {e}. Trying backup.')
            backup = get_backup_provider()
            if backup:
                for chunk in backup.generate_stream(history, system_prompt):
                    full_response.append(chunk)
                    yield chunk
            else:
                error_msg = 'AI service is temporarily unavailable. Please try again.'
                full_response.append(error_msg)
                yield error_msg

        response_time_ms = int((time.time() - start_time) * 1000)
        complete_text = ''.join(full_response)

        ChatService.add_message(
            session_id=session_id,
            role='assistant',
            content=complete_text,
            provider_used=provider_slug,
            model_used=model_name,
            response_time_ms=response_time_ms,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        AnalyticsService.track(
            event_type='chat',
            user_id=user_id,
            department_id=dept_id,
            subject_id=subject_id,
            event_data={'response_time_ms': response_time_ms, 'streaming': True},
            ip=ip_address,
            ua=user_agent,
        )
        AnalyticsService.track_question(user_message, dept_id, subject_id)
