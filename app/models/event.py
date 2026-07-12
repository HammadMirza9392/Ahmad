"""
Event Model
Institution events and activities.
"""
from datetime import datetime
from app import db


class Event(db.Model):
    __tablename__ = 'events'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(500), nullable=False)
    slug = db.Column(db.String(500), unique=True, nullable=False, index=True)
    description = db.Column(db.Text)
    content = db.Column(db.Text)
    image = db.Column(db.String(500))

    venue = db.Column(db.String(500))
    event_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)

    department_id = db.Column(db.Integer, db.ForeignKey('departments.id', ondelete='SET NULL'))

    is_active = db.Column(db.Boolean, default=True)
    is_featured = db.Column(db.Boolean, default=False)

    created_by = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='events')
    author = db.relationship('User', backref='events')

    def __repr__(self):
        return f'<Event {self.title}>'
