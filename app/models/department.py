"""
Department Model
Academic departments within the institution.
"""
from datetime import datetime
from app import db


class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    image = db.Column(db.String(500))

    # Leadership
    hod_name = db.Column(db.String(255))
    hod_image = db.Column(db.String(500))
    hod_message = db.Column(db.Text)
    hod_email = db.Column(db.String(255))
    hod_phone = db.Column(db.String(50))

    # Display
    sort_order = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    programs = db.relationship('Program', backref='department', lazy=True, cascade='all, delete-orphan')
    subjects = db.relationship('Subject', backref='department', lazy=True)

    def __repr__(self):
        return f'<Department {self.name}>'
