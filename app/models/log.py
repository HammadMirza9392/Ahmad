"""
Audit Log Model
Tracks all significant system actions for security and accountability.
"""
from datetime import datetime
from app import db


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'))
    action = db.Column(db.String(255), nullable=False)  # login, logout, create, update, delete, export, etc.
    resource_type = db.Column(db.String(100))  # user, department, knowledge, etc.
    resource_id = db.Column(db.Integer)
    details = db.Column(db.Text)

    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.String(500))

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # Relationships
    user = db.relationship('User', backref='audit_logs')

    def __repr__(self):
        return f'<AuditLog {self.action} by user {self.user_id}>'
