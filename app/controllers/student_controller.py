"""
Student Controller
Processes student panel requests — chat, quizzes, flashcards, downloads.
"""
from flask import request
from flask_login import current_user

from app.services.chat_service import ChatService
from app.services.notification_service import NotificationService
from app.services.download_service import DownloadService
from app.services.department_service import DepartmentService
from app.ai.context_manager import ContextManager


class StudentController:

    @staticmethod
    def get_dashboard_data():
        user = current_user
        sessions = ChatService.get_user_sessions(user.id)
        unread = NotificationService.unread_count(user.id)
        subjects = DepartmentService.get_subjects_for_semester(user.semester_id) if user.semester_id else []
        return {
            'recent_chats': sessions[:5],
            'total_chats': len(sessions),
            'unread_notifications': unread,
            'subjects': subjects,
        }

    @staticmethod
    def send_message(session_id, message, subject_id=None, user=None, ip=None, ua=None):
        """Process a chat message through the AI pipeline."""
        user = user or current_user._get_current_object()
        return ContextManager.process_message(
            user=user,
            session_id=session_id,
            user_message=message,
            subject_id=subject_id,
            ip_address=ip or request.remote_addr,
            user_agent=ua or request.user_agent.string,
        )
