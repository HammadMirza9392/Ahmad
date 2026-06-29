"""
Chat Service
Manages chat sessions, messages, bookmarks, and conversation history.
"""
from datetime import datetime
from app import db
from app.models.chat import ChatSession, ChatMessage


class ChatService:

    # ───────────── SESSIONS ─────────────

    @staticmethod
    def create_session(user_id, title='New Chat', department_id=None, program_id=None,
                       class_id=None, subject_id=None):
        session = ChatSession(
            user_id=user_id,
            title=title,
            department_id=department_id,
            program_id=program_id,
            class_id=class_id,
            subject_id=subject_id,
        )
        db.session.add(session)
        db.session.commit()
        return session

    @staticmethod
    def get_session(session_id, user_id=None):
        q = ChatSession.query.filter_by(id=session_id)
        if user_id:
            q = q.filter_by(user_id=user_id)
        return q.first()

    @staticmethod
    def get_user_sessions(user_id, search=None):
        q = ChatSession.query.filter_by(user_id=user_id, is_active=True).order_by(
            ChatSession.updated_at.desc()
        )
        if search:
            q = q.filter(ChatSession.title.ilike(f'%{search}%'))
        return q.all()

    @staticmethod
    def rename_session(session_id, user_id, new_title):
        session = ChatService.get_session(session_id, user_id)
        if session:
            session.title = new_title
            db.session.commit()
        return session

    @staticmethod
    def toggle_bookmark(session_id, user_id):
        session = ChatService.get_session(session_id, user_id)
        if session:
            session.is_bookmarked = not session.is_bookmarked
            db.session.commit()
        return session

    @staticmethod
    def delete_session(session_id, user_id):
        session = ChatService.get_session(session_id, user_id)
        if session:
            db.session.delete(session)
            db.session.commit()
            return True
        return False

    # ───────────── MESSAGES ─────────────

    @staticmethod
    def add_message(session_id, role, content, provider_used=None, model_used=None,
                    response_time_ms=None, tokens_used=None, ip_address=None, user_agent=None):
        msg = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
            provider_used=provider_used,
            model_used=model_used,
            response_time_ms=response_time_ms,
            tokens_used=tokens_used,
            ip_address=ip_address,
            user_agent=user_agent,
        )
        db.session.add(msg)
        # Update session timestamp
        session = db.session.get(ChatSession, session_id)
        if session:
            session.updated_at = datetime.utcnow()
        db.session.commit()
        return msg

    @staticmethod
    def get_messages(session_id, limit=50):
        return ChatMessage.query.filter_by(session_id=session_id).order_by(
            ChatMessage.created_at.asc()
        ).limit(limit).all()

    @staticmethod
    def get_conversation_history(session_id, limit=20):
        """Get recent messages formatted for AI conversation context."""
        messages = ChatMessage.query.filter_by(session_id=session_id).order_by(
            ChatMessage.created_at.desc()
        ).limit(limit).all()
        messages.reverse()
        return [{'role': m.role, 'content': m.content} for m in messages]

    @staticmethod
    def feedback_message(message_id, is_liked):
        msg = db.session.get(ChatMessage, message_id)
        if msg:
            msg.is_liked = is_liked
            db.session.commit()
        return msg

    # ───────────── ADMIN ─────────────

    @staticmethod
    def get_all_chats(page=1, per_page=20, search=None, user_id=None, date_from=None, date_to=None):
        """Admin: paginated list of all chat sessions with filters."""
        from app.models.user import User
        q = ChatSession.query.join(User).order_by(ChatSession.updated_at.desc())
        if search:
            like = f'%{search}%'
            q = q.filter(
                db.or_(
                    ChatSession.title.ilike(like),
                    User.full_name.ilike(like),
                    User.email.ilike(like),
                )
            )
        if user_id:
            q = q.filter(ChatSession.user_id == user_id)
        if date_from:
            q = q.filter(ChatSession.created_at >= date_from)
        if date_to:
            q = q.filter(ChatSession.created_at <= date_to)
        return q.paginate(page=page, per_page=per_page, error_out=False)

    @staticmethod
    def count_sessions():
        return ChatSession.query.count()

    @staticmethod
    def count_messages():
        return ChatMessage.query.count()
