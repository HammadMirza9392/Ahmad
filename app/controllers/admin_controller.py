"""
Admin Controller
Processes admin panel requests — dashboard stats, CRUD operations.
"""
from flask import request
from flask_login import current_user

from app.services.analytics_service import AnalyticsService
from app.services.institution_service import InstitutionService
from app.services.department_service import DepartmentService
from app.services.student_service import StudentService
from app.services.knowledge_service import KnowledgeService
from app.services.ai_service import AIService
from app.services.notification_service import NotificationService
from app.services.download_service import DownloadService
from app.services.cms_service import CMSService
from app.services.search_service import SearchService
from app.utils.file_handler import save_upload


class AdminController:

    # ───────────── DASHBOARD ─────────────

    @staticmethod
    def get_dashboard_data():
        stats = AnalyticsService.get_dashboard_stats()
        daily_chats = AnalyticsService.get_daily_chats(7)
        weekly_chats = AnalyticsService.get_weekly_chats(4)
        monthly_chats = AnalyticsService.get_monthly_chats(12)
        trending = AnalyticsService.get_trending_questions(10)
        active_students = AnalyticsService.get_most_active_students(10)
        active_depts = AnalyticsService.get_most_active_departments(10)
        ai_usage = AnalyticsService.get_ai_usage(30)
        return {
            'stats': stats,
            'daily_chats': daily_chats,
            'weekly_chats': weekly_chats,
            'monthly_chats': monthly_chats,
            'trending': trending,
            'active_students': active_students,
            'active_depts': active_depts,
            'ai_usage': ai_usage,
        }

    # ───────────── INSTITUTION ─────────────

    @staticmethod
    def get_institution():
        return InstitutionService.get_or_create()

    @staticmethod
    def update_institution(data, files=None):
        inst = InstitutionService.get_or_create()
        # Handle file uploads
        if files:
            for field in ['logo', 'banner', 'favicon', 'principal_image', 'vc_image']:
                file = files.get(field)
                if file and file.filename:
                    filename, path, size = save_upload(file, 'institution')
                    if filename:
                        data[field] = f'/static/uploads/institution/{filename}'
        return InstitutionService.update(inst, data)

    # ───────────── GLOBAL SEARCH ─────────────

    @staticmethod
    def search(query):
        return SearchService.global_search(query)
