"""
Subject Model
Academic subjects that belong to departments and are assigned to a semester.
"""
from datetime import datetime
from app import db


class Subject(db.Model):
    __tablename__ = 'subjects'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, index=True)
    code = db.Column(db.String(50))
    description = db.Column(db.Text)
    credit_hours = db.Column(db.Integer)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    semester_id = db.Column(db.Integer, db.ForeignKey('semesters.id'), nullable=True)
    # Single teacher per subject kept intentionally (see migration notes) —
    # multi-teacher support was explicitly optional in the spec.
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    knowledge_entries = db.relationship('KnowledgeBase', backref='subject', lazy='dynamic')
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='taught_subjects')

    def __repr__(self):
        return f'<Subject {self.name}>'
