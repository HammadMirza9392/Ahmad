"""
Program Model
Academic programs offered by departments (e.g., ICS, BSc, BA).
"""
from datetime import datetime
from app import db


class Program(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    duration = db.Column(db.String(50))  # e.g., "2 Years", "4 Years"
    degree_type = db.Column(db.String(100))  # Intermediate, Bachelor, Master

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    classes = db.relationship('Class', backref='program', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Program {self.name}>'
