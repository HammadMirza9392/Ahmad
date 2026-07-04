"""
Scope Checks
Helpers that re-derive access scope from the DB record, never trusting a URL id.
"""
from flask import abort
from flask_login import current_user

from app import db
from app.models.subject import Subject


def require_department_scope(department_id):
    """HOD may only act within their own department. Admins bypass."""
    if current_user.is_admin():
        return
    if not current_user.is_hod() or current_user.department_id != department_id:
        abort(403)


def require_subject_ownership(subject_id):
    """Return the Subject if the current user may act on it, else 403.
    - Teacher: must own subject.teacher_id.
    - HOD: subject must be in their department.
    - Admin: always allowed.
    """
    subject = db.session.get(Subject, subject_id)
    if not subject:
        abort(404)
    if current_user.is_admin():
        return subject
    if current_user.is_teacher() and subject.teacher_id == current_user.id:
        return subject
    if current_user.is_hod() and subject.department_id == current_user.department_id:
        return subject
    abort(403)
