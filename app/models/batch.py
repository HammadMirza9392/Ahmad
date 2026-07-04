"""
Batch Model
Intake-year cohort under a Program (e.g., BSCS Batch 2022-2026).
"""
from datetime import datetime
from app import db


class Batch(db.Model):
    __tablename__ = 'batches'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=False, index=True)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    status = db.Column(db.String(20), default='active')  # upcoming, active, completed

    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    semesters = db.relationship('Semester', backref='batch', lazy=True, cascade='all, delete-orphan')

    @property
    def label(self):
        """Display label, e.g. '2022-2026'. Falls back to name if years unset."""
        if self.start_year and self.end_year:
            return f'{self.start_year}-{self.end_year}'
        return self.name

    def __repr__(self):
        return f'<Batch {self.name}>'
