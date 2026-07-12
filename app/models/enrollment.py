"""
Enrollment Model
Links students to subjects (auto-allocated from class or manually overridden).
"""
from datetime import datetime
from app import db


class Enrollment(db.Model):
    __tablename__ = 'enrollments'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    source = db.Column(db.String(20), default='auto')  # auto, manual
    allocated_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    allocated_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', name='uq_enrollment_student_subject'),
    )

    student = db.relationship('User', foreign_keys=[student_id],
                              backref=db.backref('enrollments', cascade='all, delete-orphan'))
    subject = db.relationship('Subject', backref=db.backref('enrollments', cascade='all, delete-orphan'))

    def __repr__(self):
        return f'<Enrollment student={self.student_id} subject={self.subject_id}>'
