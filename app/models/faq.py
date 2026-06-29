"""
FAQ Model
Frequently asked questions for the public website.
"""
from datetime import datetime
from app import db


class FAQ(db.Model):
    __tablename__ = 'faqs'

    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(1000), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100))

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))

    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='faqs')

    def __repr__(self):
        return f'<FAQ {self.question[:50]}>'
