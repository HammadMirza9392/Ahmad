"""
Teacher Controller
Processes teacher panel requests — currently just AI chat.
"""
from flask import request
from flask_login import current_user

from app.ai.context_manager import ContextManager


class TeacherController:

    @staticmethod
    def send_message(session_id, message, user=None, ip=None, ua=None):
        """Process a teacher chat message through the teacher-scoped AI pipeline."""
        user = user or current_user._get_current_object()
        return ContextManager.process_teacher_message(
            user=user,
            session_id=session_id,
            user_message=message,
            ip_address=ip or request.remote_addr,
            user_agent=ua or request.user_agent.string,
        )
