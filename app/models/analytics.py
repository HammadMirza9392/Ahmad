"""
Analytics Model
Tracks usage metrics, AI requests, and trending data.
"""
from datetime import datetime
from app import db


class AnalyticsEvent(db.Model):
    __tablename__ = 'analytics_events'

    id = db.Column(db.Integer, primary_key=True)
    event_type = db.Column(db.String(100), nullable=False, index=True)  # chat, login, download, search, quiz
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))

    # Event data stored as JSON text
    event_data = db.Column(db.Text)

    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))
    device_type = db.Column(db.String(50))  # desktop, mobile, tablet

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref='analytics_events')

    def __repr__(self):
        return f'<AnalyticsEvent {self.event_type}>'


class TrendingQuestion(db.Model):
    """Pre-aggregated trending questions for dashboard performance."""
    __tablename__ = 'trending_questions'

    id = db.Column(db.Integer, primary_key=True)
    question_text = db.Column(db.String(1000), nullable=False)
    normalized_text = db.Column(db.String(1000), index=True)
    count = db.Column(db.Integer, default=1)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'))
    last_asked = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TrendingQuestion {self.question_text[:50]}>'
