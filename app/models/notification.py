"""
Notification Model
System notifications targeted to departments, classes, or all students.
"""
from datetime import datetime
from app import db


class Notification(db.Model):
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    content = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # news, exam, admission, assignment, holiday, scholarship, result

    # Targeting
    target_type = db.Column(db.String(50), default='all')  # all, department, batch, semester
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'))
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id', ondelete='SET NULL'))
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id', ondelete='SET NULL'))

    is_active = db.Column(db.Boolean, default=True)
    priority = db.Column(db.String(20), default='normal')  # low, normal, high, urgent

    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)

    # Relationships
    author = db.relationship('User', backref='created_notifications')
    user_notifications = db.relationship('UserNotification', backref='notification', lazy='dynamic',
                                         cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Notification {self.title}>'


class UserNotification(db.Model):
    """Tracks which users have read which notifications."""
    __tablename__ = 'user_notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    notification_id = db.Column(db.Integer, db.ForeignKey('notifications.id', ondelete='CASCADE'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    read_at = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'notification_id', name='uq_user_notification'),
    )
