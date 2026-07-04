"""
Custom Decorators
Role-based access control and other route guards.
"""
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(f):
    """Restrict access to admin and super_admin users."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def super_admin_required(f):
    """Restrict access to super_admin users only."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_super_admin():
            abort(403)
        return f(*args, **kwargs)
    return decorated


def student_required(f):
    """Restrict access to student users."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'student':
            abort(403)
        return f(*args, **kwargs)
    return decorated


def hod_required(f):
    """Restrict access to HOD users (or admins acting on their behalf)."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_hod() or current_user.is_admin()):
            abort(403)
        return f(*args, **kwargs)
    return decorated


def teacher_required(f):
    """Restrict access to teacher users."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not (current_user.is_teacher() or current_user.is_admin()):
            abort(403)
        return f(*args, **kwargs)
    return decorated
