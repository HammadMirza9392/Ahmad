"""
Authentication Service
Handles user registration, login, password hashing, and token generation.
"""
import secrets
from datetime import datetime, timedelta
import bcrypt
from flask import current_app
from flask_mail import Message

from app import db, mail
from app.models.user import User
from app.models.log import AuditLog


class AuthService:

    @staticmethod
    def hash_password(password):
        """Generate bcrypt hash for a password."""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    @staticmethod
    def verify_password(password, password_hash):
        """Verify a password against its bcrypt hash."""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def authenticate(email, password):
        """Authenticate user by email and password. Returns (user, error_message)."""
        user = User.query.filter_by(email=email.lower().strip()).first()
        if not user:
            return None, 'Invalid email or password.'
        if not user.is_active:
            return None, 'Your account has been deactivated. Contact administrator.'
        if not AuthService.verify_password(password, user.password_hash):
            return None, 'Invalid email or password.'
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        return user, None

    @staticmethod
    def create_user(email, password, full_name, role='student', **kwargs):
        """Create a new user account. Returns (user, error_message)."""
        if User.query.filter_by(email=email.lower().strip()).first():
            return None, 'An account with this email already exists.'
        user = User(
            email=email.lower().strip(),
            password_hash=AuthService.hash_password(password),
            full_name=full_name,
            role=role,
            **kwargs,
        )
        db.session.add(user)
        db.session.commit()
        return user, None

    @staticmethod
    def change_password(user, current_password, new_password):
        """Change user password. Returns (success, message)."""
        if not AuthService.verify_password(current_password, user.password_hash):
            return False, 'Current password is incorrect.'
        user.password_hash = AuthService.hash_password(new_password)
        db.session.commit()
        return True, 'Password changed successfully.'

    @staticmethod
    def generate_reset_token(email):
        """Generate a password reset token and send email. Returns (success, message)."""
        user = User.query.filter_by(email=email.lower().strip()).first()
        if not user:
            return True, 'If that email exists, a reset link has been sent.'
        token = secrets.token_urlsafe(48)
        user.password_reset_token = token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        try:
            msg = Message(
                'Password Reset Request',
                recipients=[user.email],
                html=f'''
                <h2>Password Reset</h2>
                <p>Hi {user.full_name},</p>
                <p>You requested a password reset. Use this token to reset your password:</p>
                <p><strong>{token}</strong></p>
                <p>This token expires in 1 hour.</p>
                <p>If you did not request this, ignore this email.</p>
                '''
            )
            mail.send(msg)
        except Exception:
            pass  # Email sending is best-effort

        return True, 'If that email exists, a reset link has been sent.'

    @staticmethod
    def reset_password(token, new_password):
        """Reset password using a valid token. Returns (success, message)."""
        user = User.query.filter_by(password_reset_token=token).first()
        if not user:
            return False, 'Invalid or expired reset token.'
        if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
            return False, 'Reset token has expired. Please request a new one.'
        user.password_hash = AuthService.hash_password(new_password)
        user.password_reset_token = None
        user.password_reset_expires = None
        db.session.commit()
        return True, 'Password has been reset. You can now log in.'

    @staticmethod
    def log_action(user_id, action, resource_type=None, resource_id=None, details=None, ip=None, ua=None):
        """Record an audit log entry."""
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip,
            user_agent=ua,
        )
        db.session.add(log)
        db.session.commit()
