"""
Auth Controller
Processes authentication requests and prepares responses.
"""
from flask import request, flash, redirect, url_for, session
from flask_login import login_user, logout_user, current_user

from app.services.auth_service import AuthService
from app.utils.validators import validate_email, validate_password


class AuthController:

    @staticmethod
    def handle_login():
        """Process login form. Returns redirect response or (None, error) for re-render."""
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'

        if not email or not password:
            return None, 'Please fill in all fields.'

        user, error = AuthService.authenticate(email, password)
        if error:
            return None, error

        login_user(user, remember=remember)
        session.permanent = True

        AuthService.log_action(user.id, 'login', ip=request.remote_addr, ua=request.user_agent.string)

        if user.is_admin():
            return redirect(url_for('admin.dashboard')), None
        if user.is_hod():
            return redirect(url_for('hod.dashboard')), None
        if user.is_teacher():
            return redirect(url_for('teacher.dashboard')), None
        return redirect(url_for('student.dashboard')), None

    @staticmethod
    def handle_logout():
        if current_user.is_authenticated:
            AuthService.log_action(current_user.id, 'logout', ip=request.remote_addr,
                                   ua=request.user_agent.string)
        logout_user()
        flash('You have been logged out.', 'info')
        return redirect(url_for('auth.login'))

    @staticmethod
    def handle_forgot_password():
        email = request.form.get('email', '').strip()
        if not validate_email(email):
            return None, 'Please enter a valid email address.'
        success, msg = AuthService.generate_reset_token(email)
        return success, msg

    @staticmethod
    def handle_reset_password():
        token = request.form.get('token', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')

        if password != confirm:
            return False, 'Passwords do not match.'
        valid, msg = validate_password(password)
        if not valid:
            return False, msg
        return AuthService.reset_password(token, password)

    @staticmethod
    def handle_change_password():
        current_pw = request.form.get('current_password', '')
        new_pw = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')

        if new_pw != confirm:
            return False, 'New passwords do not match.'
        valid, msg = validate_password(new_pw)
        if not valid:
            return False, msg
        return AuthService.change_password(current_user, current_pw, new_pw)
