"""
User Model
Handles authentication, roles, and student profile data.
"""
from datetime import datetime
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')  # super_admin, admin, student

    # Profile
    full_name = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20))
    avatar = db.Column(db.String(500))
    roll_number = db.Column(db.String(50), index=True)

    # Academic context (for students)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    program_id = db.Column(db.Integer, db.ForeignKey('programs.id'))
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'))
    semester = db.Column(db.String(20))

    # Status
    is_active = db.Column(db.Boolean, default=True)
    email_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    password_reset_token = db.Column(db.String(255))
    password_reset_expires = db.Column(db.DateTime)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    department = db.relationship('Department', backref='students', lazy=True)
    program = db.relationship('Program', backref='students', lazy=True)
    student_class = db.relationship('Class', backref='students', lazy=True)
    chat_sessions = db.relationship('ChatSession', backref='user', lazy='dynamic')
    notifications = db.relationship('UserNotification', backref='user', lazy='dynamic')

    def is_admin(self):
        return self.role in ('super_admin', 'admin')

    def is_super_admin(self):
        return self.role == 'super_admin'

    def __repr__(self):
        return f'<User {self.email}>'
