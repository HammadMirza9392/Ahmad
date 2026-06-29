"""
Analytics Service
Tracks events and generates dashboard statistics.
"""
import json
from datetime import datetime, timedelta
from sqlalchemy import func, desc

from app import db
from app.models.analytics import AnalyticsEvent, TrendingQuestion
from app.models.chat import ChatSession, ChatMessage
from app.models.user import User
from app.models.knowledge_base import KnowledgeBase
from app.models.department import Department
from app.models.subject import Subject
from app.models.download import Download
from app.utils.helpers import get_device_type


class AnalyticsService:

    # ───────────── EVENT TRACKING ─────────────

    @staticmethod
    def track(event_type, user_id=None, department_id=None, subject_id=None,
              event_data=None, ip=None, ua=None):
        evt = AnalyticsEvent(
            event_type=event_type,
            user_id=user_id,
            department_id=department_id,
            subject_id=subject_id,
            event_data=json.dumps(event_data) if event_data else None,
            ip_address=ip,
            user_agent=ua,
            device_type=get_device_type(ua),
        )
        db.session.add(evt)
        db.session.commit()

    @staticmethod
    def track_question(question_text, department_id=None, subject_id=None):
        """Increment trending question counter or create new entry."""
        normalized = question_text.lower().strip()[:500]
        existing = TrendingQuestion.query.filter_by(normalized_text=normalized).first()
        if existing:
            existing.count += 1
            existing.last_asked = datetime.utcnow()
        else:
            tq = TrendingQuestion(
                question_text=question_text[:1000],
                normalized_text=normalized,
                count=1,
                department_id=department_id,
                subject_id=subject_id,
            )
            db.session.add(tq)
        db.session.commit()

    # ───────────── DASHBOARD STATS ─────────────

    @staticmethod
    def get_dashboard_stats():
        """Return dictionary of counts for admin dashboard cards."""
        return {
            'total_students': User.query.filter_by(role='student').count(),
            'total_departments': Department.query.filter_by(is_active=True).count(),
            'total_subjects': Subject.query.filter_by(is_active=True).count(),
            'total_chats': ChatSession.query.count(),
            'ai_requests': ChatMessage.query.filter_by(role='assistant').count(),
            'active_users': User.query.filter(
                User.last_login >= datetime.utcnow() - timedelta(days=7)
            ).count(),
            'total_downloads': Download.query.count(),
            'knowledge_records': KnowledgeBase.query.filter_by(status='published').count(),
        }

    # ───────────── CHART DATA ─────────────

    @staticmethod
    def get_daily_chats(days=7):
        """Chat counts per day for the last N days."""
        since = datetime.utcnow() - timedelta(days=days)
        rows = db.session.query(
            func.date(ChatSession.created_at).label('day'),
            func.count(ChatSession.id),
        ).filter(ChatSession.created_at >= since).group_by('day').order_by('day').all()
        return [{'date': str(r[0]), 'count': r[1]} for r in rows]

    @staticmethod
    def get_weekly_chats(weeks=4):
        since = datetime.utcnow() - timedelta(weeks=weeks)
        rows = db.session.query(
            func.date_trunc('week', ChatSession.created_at).label('week'),
            func.count(ChatSession.id),
        ).filter(ChatSession.created_at >= since).group_by('week').order_by('week').all()
        return [{'week': str(r[0].date()) if r[0] else '', 'count': r[1]} for r in rows]

    @staticmethod
    def get_monthly_chats(months=12):
        since = datetime.utcnow() - timedelta(days=months * 30)
        rows = db.session.query(
            func.date_trunc('month', ChatSession.created_at).label('month'),
            func.count(ChatSession.id),
        ).filter(ChatSession.created_at >= since).group_by('month').order_by('month').all()
        return [{'month': r[0].strftime('%b %Y') if r[0] else '', 'count': r[1]} for r in rows]

    @staticmethod
    def get_trending_questions(limit=10, days=30):
        since = datetime.utcnow() - timedelta(days=days)
        return TrendingQuestion.query.filter(
            TrendingQuestion.last_asked >= since
        ).order_by(desc(TrendingQuestion.count)).limit(limit).all()

    @staticmethod
    def get_most_active_students(limit=10, days=30):
        since = datetime.utcnow() - timedelta(days=days)
        rows = db.session.query(
            User.full_name,
            User.roll_number,
            func.count(ChatSession.id).label('chat_count'),
        ).join(ChatSession, ChatSession.user_id == User.id).filter(
            ChatSession.created_at >= since
        ).group_by(User.id, User.full_name, User.roll_number).order_by(
            desc('chat_count')
        ).limit(limit).all()
        return [{'name': r[0], 'roll': r[1] or '', 'chats': r[2]} for r in rows]

    @staticmethod
    def get_most_active_departments(limit=10, days=30):
        since = datetime.utcnow() - timedelta(days=days)
        rows = db.session.query(
            Department.name,
            func.count(ChatSession.id).label('chat_count'),
        ).join(ChatSession, ChatSession.department_id == Department.id).filter(
            ChatSession.created_at >= since
        ).group_by(Department.id, Department.name).order_by(
            desc('chat_count')
        ).limit(limit).all()
        return [{'name': r[0], 'chats': r[1]} for r in rows]

    @staticmethod
    def get_ai_usage(days=30):
        """AI provider usage breakdown."""
        since = datetime.utcnow() - timedelta(days=days)
        rows = db.session.query(
            ChatMessage.provider_used,
            func.count(ChatMessage.id),
        ).filter(
            ChatMessage.role == 'assistant',
            ChatMessage.created_at >= since,
        ).group_by(ChatMessage.provider_used).all()
        return [{'provider': r[0] or 'Unknown', 'count': r[1]} for r in rows]
