"""
Assignment Models
A teacher-posted assignment with a due date, and per-student submissions.
"""
from datetime import datetime
from app import db


class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_url = db.Column(db.String(500))  # optional attachment from the teacher
    due_date = db.Column(db.DateTime, nullable=False)
    total_marks = db.Column(db.Integer)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    subject = db.relationship('Subject', backref='assignments')
    teacher = db.relationship('User', backref='assignments')
    submissions = db.relationship('AssignmentSubmission', backref='assignment', lazy=True,
                                  cascade='all, delete-orphan')

    @property
    def is_past_due(self):
        return datetime.utcnow() > self.due_date

    def __repr__(self):
        return f'<Assignment {self.title}>'


class AssignmentSubmission(db.Model):
    __tablename__ = 'assignment_submissions'

    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignments.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    file_url = db.Column(db.String(500), nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    marks_awarded = db.Column(db.Integer)
    feedback = db.Column(db.Text)
    graded_at = db.Column(db.DateTime)

    student = db.relationship('User', backref='assignment_submissions')

    __table_args__ = (
        db.UniqueConstraint('assignment_id', 'student_id', name='uq_assignment_student'),
    )

    @property
    def is_late(self):
        return self.submitted_at > self.assignment.due_date

    @property
    def is_graded(self):
        return self.marks_awarded is not None

    def __repr__(self):
        return f'<AssignmentSubmission assignment={self.assignment_id} student={self.student_id}>'
