"""
Class Model
Represents academic classes/years within programs (e.g., Part 1, Part 2, Semester 1).
"""
from datetime import datetime
from app import db


class Class(db.Model):
    __tablename__ = 'classes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, index=True)
    section = db.Column(db.String(50))
    year = db.Column(db.String(50))

    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    subjects = db.relationship('ClassSubject', backref='class_obj', lazy=True)

    def __repr__(self):
        return f'<Class {self.name}>'


class ClassSubject(db.Model):
    """Many-to-many bridge: which subjects are taught in which class."""
    __tablename__ = 'class_subjects'

    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)

    __table_args__ = (
        db.UniqueConstraint('class_id', 'subject_id', name='uq_class_subject'),
    )
