"""
Subject Model
Academic subjects that belong to departments and are assigned to classes.
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

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    knowledge_entries = db.relationship('KnowledgeBase', backref='subject', lazy='dynamic')
    class_subjects = db.relationship('ClassSubject', backref='subject', lazy=True)

    def __repr__(self):
        return f'<Subject {self.name}>'
