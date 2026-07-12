"""
Semester Model
Replaces the old Class model. A term within a Batch (e.g., Semester 3).
Subjects and students attach directly at this level.
"""
from datetime import datetime, date
from app import db


class Semester(db.Model):
    __tablename__ = 'semesters'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, index=True)
    number = db.Column(db.Integer)  # e.g., 1-8
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)

    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id', ondelete='CASCADE'), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    # NOTE: no ORM-level delete-orphan cascade — subjects can be reassigned to a different semester
    # (see DepartmentService.update_subject), and delete-orphan would delete the Subject the moment
    # it's disassociated from its current semester. Deleting the semester itself is instead handled
    # at the DB level via subjects.semester_id's ondelete='CASCADE'.
    subjects = db.relationship('Subject', backref='semester', lazy=True)

    @property
    def status(self):
        """Derive upcoming/active/completed from dates when available,
        else fall back to the manually-set is_active flag."""
        today = date.today()
        if self.start_date and self.end_date:
            if today < self.start_date:
                return 'upcoming'
            if today > self.end_date:
                return 'completed'
            return 'active'
        return 'active' if self.is_active else 'completed'

    def __repr__(self):
        return f'<Semester {self.name}>'
