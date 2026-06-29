"""
Search Service
Global search across students, departments, subjects, knowledge, chats, files.
"""
from app import db
from app.models.user import User
from app.models.department import Department
from app.models.subject import Subject
from app.models.knowledge_base import KnowledgeBase
from app.models.chat import ChatSession
from app.models.download import Download


class SearchService:

    @staticmethod
    def global_search(query, limit=10):
        """Search across all major entities. Returns categorized results."""
        if not query or len(query) < 2:
            return {}

        like = f'%{query}%'
        results = {}

        # Students
        students = User.query.filter(
            User.role == 'student',
            db.or_(User.full_name.ilike(like), User.email.ilike(like), User.roll_number.ilike(like)),
        ).limit(limit).all()
        if students:
            results['students'] = [
                {'id': s.id, 'name': s.full_name, 'email': s.email, 'roll': s.roll_number}
                for s in students
            ]

        # Departments
        departments = Department.query.filter(
            db.or_(Department.name.ilike(like), Department.description.ilike(like))
        ).limit(limit).all()
        if departments:
            results['departments'] = [
                {'id': d.id, 'name': d.name, 'slug': d.slug}
                for d in departments
            ]

        # Subjects
        subjects = Subject.query.filter(
            db.or_(Subject.name.ilike(like), Subject.code.ilike(like))
        ).limit(limit).all()
        if subjects:
            results['subjects'] = [
                {'id': s.id, 'name': s.name, 'code': s.code}
                for s in subjects
            ]

        # Knowledge Base
        knowledge = KnowledgeBase.query.filter(
            db.or_(KnowledgeBase.title.ilike(like), KnowledgeBase.content.ilike(like))
        ).limit(limit).all()
        if knowledge:
            results['knowledge'] = [
                {'id': k.id, 'title': k.title, 'status': k.status}
                for k in knowledge
            ]

        # Chats
        chats = ChatSession.query.filter(ChatSession.title.ilike(like)).limit(limit).all()
        if chats:
            results['chats'] = [
                {'id': c.id, 'title': c.title, 'user_id': c.user_id}
                for c in chats
            ]

        # Downloads
        downloads = Download.query.filter(
            db.or_(Download.title.ilike(like), Download.description.ilike(like))
        ).limit(limit).all()
        if downloads:
            results['downloads'] = [
                {'id': d.id, 'title': d.title, 'category': d.category}
                for d in downloads
            ]

        return results
