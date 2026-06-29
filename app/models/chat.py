"""
Chat Models
Stores chat sessions, messages, bookmarks, and interaction metadata.
"""
from datetime import datetime
from app import db


class ChatSession(db.Model):
    __tablename__ = 'chat_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    title = db.Column(db.String(500), default='New Chat')

    # Context snapshot at session creation
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))

    is_bookmarked = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy='dynamic',
                               cascade='all, delete-orphan', order_by='ChatMessage.created_at')

    def __repr__(self):
        return f'<ChatSession {self.id} - {self.title}>'


class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.Integer, db.ForeignKey('chat_sessions.id'), nullable=False, index=True)
    role = db.Column(db.String(20), nullable=False)  # user, assistant
    content = db.Column(db.Text, nullable=False)

    # AI metadata
    provider_used = db.Column(db.String(100))
    model_used = db.Column(db.String(255))
    response_time_ms = db.Column(db.Integer)
    tokens_used = db.Column(db.Integer)

    # Feedback
    is_liked = db.Column(db.Boolean)
    feedback = db.Column(db.Text)

    # Client metadata
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ChatMessage {self.id} [{self.role}]>'
