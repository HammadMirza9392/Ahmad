"""
Announcement Model
Scoped announcements: university-wide, department, or subject.
"""
from datetime import datetime
from app import db


class Announcement(db.Model):
    __tablename__ = 'announcements'

    id = db.Column(db.Integer, primary_key=True)
    scope_type = db.Column(db.String(20), default='subject')  # university, department, subject
    scope_id = db.Column(db.Integer, nullable=True)  # department_id or subject_id (null for university)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    body = db.Column(db.Text)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref='announcements')

    def __repr__(self):
        return f'<Announcement {self.title} scope={self.scope_type}>'
