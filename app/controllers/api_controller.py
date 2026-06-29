"""
API Controller
Handles AJAX endpoints — chat, search, analytics, dynamic form loading.
"""
from flask import jsonify, request
from flask_login import current_user

from app.services.search_service import SearchService
from app.services.department_service import DepartmentService
from app.services.notification_service import NotificationService


class APIController:

    @staticmethod
    def search():
        query = request.args.get('q', '').strip()
        results = SearchService.global_search(query)
        return jsonify(results)

    @staticmethod
    def get_programs_for_department():
        dept_id = request.args.get('department_id', type=int)
        if not dept_id:
            return jsonify([])
        programs = DepartmentService.get_programs(department_id=dept_id, active_only=True)
        return jsonify([{'id': p.id, 'name': p.name} for p in programs])

    @staticmethod
    def get_classes_for_program():
        prog_id = request.args.get('program_id', type=int)
        if not prog_id:
            return jsonify([])
        classes = DepartmentService.get_classes(program_id=prog_id, active_only=True)
        return jsonify([{'id': c.id, 'name': c.name} for c in classes])

    @staticmethod
    def get_subjects_for_department():
        dept_id = request.args.get('department_id', type=int)
        if not dept_id:
            return jsonify([])
        subjects = DepartmentService.get_subjects(department_id=dept_id, active_only=True)
        return jsonify([{'id': s.id, 'name': s.name} for s in subjects])

    @staticmethod
    def mark_notification_read():
        notif_id = request.json.get('notification_id')
        if notif_id and current_user.is_authenticated:
            NotificationService.mark_read(current_user.id, notif_id)
        return jsonify({'status': 'ok'})
