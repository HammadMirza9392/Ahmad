"""
API Routes
AJAX endpoints for search, dynamic data loading, notifications, and public chatbot.
"""
import logging
import traceback
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

from app import csrf
from app.controllers.api_controller import APIController

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)


@api_bp.route('/search')
@login_required
def search():
    return APIController.search()


@api_bp.route('/programs')
def programs():
    return APIController.get_programs_for_department()


@api_bp.route('/classes')
def classes():
    return APIController.get_classes_for_program()


@api_bp.route('/subjects')
def subjects():
    return APIController.get_subjects_for_department()


@api_bp.route('/notifications/read', methods=['POST'])
@login_required
def notification_read():
    return APIController.mark_notification_read()


@api_bp.route('/public-chat', methods=['POST'])
def public_chat():
    """Public chatbot. Logged-in students get context-aware answers.
    Logged-out users get general institution answers."""
    data = request.get_json()
    if not data:
        return jsonify({'response': 'Please type a question.'})
    message = data.get('message', '').strip()
    if not message:
        return jsonify({'response': 'Please type a question.'})

    try:
        from app.ai.provider_factory import get_provider
        from app.models.institution import Institution

        institution = Institution.query.first()
        inst_name = institution.name if institution else 'the institution'

        provider = get_provider()

        if current_user.is_authenticated and current_user.role == 'student':
            from app.ai.context_manager import ContextManager
            from app.services.chat_service import ChatService

            session = ChatService.create_session(
                user_id=current_user.id,
                title='Quick Chat',
                department_id=current_user.department_id,
                program_id=current_user.program_id,
                class_id=current_user.class_id,
            )
            response_text, _ = ContextManager.process_message(
                user=current_user,
                session_id=session.id,
                user_message=message,
                ip_address=request.remote_addr,
                user_agent=request.user_agent.string,
            )
        else:
            system_prompt = f"""You are a helpful AI assistant for {inst_name}.
Answer general questions about admissions, programs, departments, campus, fees, and facilities.
Keep answers brief and professional. Use 2-4 sentences maximum.
If asked about specific study material or exam content, suggest logging into the Student Portal."""

            if institution:
                system_prompt += f"""
Institution: {inst_name}
Address: {institution.address or 'N/A'}
Phone: {institution.phone or 'N/A'}
Email: {institution.email or 'N/A'}
About: {(institution.about or '')[:500]}"""

            messages = [{'role': 'user', 'content': message}]
            response_text, _ = provider.generate(messages, system_prompt)

        return jsonify({'response': response_text})

    except Exception as e:
        logger.error(f'Public chat error: {traceback.format_exc()}')
        error_msg = str(e)
        if 'No active AI provider' in error_msg:
            return jsonify({'response': 'AI assistant is not configured yet. Please contact the administrator.'})
        return jsonify({'response': f'Sorry, something went wrong. Please try again.'})
