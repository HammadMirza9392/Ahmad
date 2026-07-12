"""
Study Material Model
Teacher-uploaded materials attached to a subject.
"""
from datetime import datetime
from app import db


class StudyMaterial(db.Model):
    __tablename__ = 'study_materials'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    file_url = db.Column(db.String(500))
    material_type = db.Column(db.String(50), default='notes')  # notes, slides, reference, link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subject = db.relationship('Subject', backref=db.backref('study_materials', cascade='all, delete-orphan'))
    teacher = db.relationship('User', backref=db.backref('study_materials', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<StudyMaterial {self.title}>'
