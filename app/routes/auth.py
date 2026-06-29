"""
Authentication Routes
Handles login, logout, registration, password reset, and profile management.
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user

from app.controllers.auth_controller import AuthController

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if current_user.is_admin():
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        result, error = AuthController.handle_login()
        if error:
            flash(error, 'danger')
            return render_template('auth/login.html')
        return result

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    return AuthController.handle_logout()


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        success, msg = AuthController.handle_forgot_password()
        flash(msg, 'success' if success else 'danger')
        if success:
            return redirect(url_for('auth.login'))
    return render_template('auth/forgot_password.html')


@auth_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    token = request.args.get('token', '')
    if request.method == 'POST':
        success, msg = AuthController.handle_reset_password()
        flash(msg, 'success' if success else 'danger')
        if success:
            return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', token=token)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        from app import db
        from app.utils.file_handler import save_upload
        data = {
            'full_name': request.form.get('full_name', current_user.full_name),
            'phone': request.form.get('phone', ''),
        }
        avatar = request.files.get('avatar')
        if avatar and avatar.filename:
            filename, path, size = save_upload(avatar, 'profiles')
            if filename:
                data['avatar'] = f'/static/uploads/profiles/{filename}'
                current_user.avatar = data['avatar']
        current_user.full_name = data['full_name']
        current_user.phone = data['phone']
        db.session.commit()
        flash('Profile updated successfully.', 'success')
    return render_template('auth/profile.html')


@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        success, msg = AuthController.handle_change_password()
        flash(msg, 'success' if success else 'danger')
    return render_template('auth/change_password.html')
