"""
Application Factory
Creates and configures the Flask application instance.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from config import config_map

# Extensions initialized without app binding (factory pattern)
db = SQLAlchemy()
login_manager = LoginManager()
csrf = CSRFProtect()
mail = Mail()
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])


def create_app(config_name='development'):
    """Build and return the configured Flask application."""
    app = Flask(__name__)
    app.config.from_object(config_map.get(config_name, config_map['development']))

    # Bind extensions
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    mail.init_app(app)
    limiter.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'warning'

    # User loader for Flask-Login
    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.student import student_bp
    from app.routes.cms import cms_bp
    from app.routes.api import api_bp
    from app.routes.hod import hod_bp
    from app.routes.teacher import teacher_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(cms_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(hod_bp, url_prefix='/hod')
    app.register_blueprint(teacher_bp, url_prefix='/teacher')

    # Exempt public chat API from CSRF (called via AJAX without form)
    csrf.exempt(api_bp)

    # Context processors: inject institution, datetime, and helpers into every template
    from datetime import datetime
    from app.services.institution_service import InstitutionService
    from app.utils.helpers import render_markdown, time_ago, format_file_size

    @app.context_processor
    def inject_globals():
        try:
            institution = InstitutionService.get_institution()
        except Exception:
            institution = None
        try:
            from app.services.theme_service import ThemeService
            theme = ThemeService.get_active_theme()
        except Exception:
            theme = None
        return dict(
            institution=institution,
            theme=theme,
            now=datetime.utcnow,
        )

    # Jinja2 filters
    app.jinja_env.filters['markdown'] = render_markdown
    app.jinja_env.filters['timeago'] = time_ago
    app.jinja_env.filters['filesize'] = format_file_size
    app.jinja_env.globals['csrf_token'] = lambda: csrf._get_csrf_token()

    # Error handlers
    _register_error_handlers(app)

    # Create tables on first request (development convenience)
    with app.app_context():
        _ensure_tables(app)

    return app


def _register_error_handlers(app):
    """Attach custom error pages."""
    from flask import render_template

    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        return render_template('errors/500.html'), 500


def _ensure_tables(app):
    """Create database tables if they don't exist yet."""
    import app.models.user
    import app.models.institution
    import app.models.department
    import app.models.program
    import app.models.batch
    import app.models.semester
    import app.models.knowledge_base
    import app.models.subject
    import app.models.ai_settings
    import app.models.chat
    import app.models.analytics
    import app.models.notification
    import app.models.download
    import app.models.gallery
    import app.models.cms
    import app.models.event
    import app.models.news
    import app.models.faq
    import app.models.log
    import app.models.enrollment
    import app.models.quiz
    import app.models.theme
    import app.models.study_material
    import app.models.announcement
    import app.models.assignment
    db.create_all()
    _drop_legacy_class_tables()
    _ensure_new_columns()


def _drop_legacy_class_tables():
    """Remove legacy class tables from the database if they still exist."""
    from sqlalchemy import text
    try:
        with db.engine.begin() as conn:
            conn.execute(text('DROP TABLE IF EXISTS class_subjects'))
            conn.execute(text('DROP TABLE IF EXISTS classes'))
    except Exception:
        db.session.rollback()


def _ensure_new_columns():
    """Add columns introduced on existing tables (no Alembic in this project).
    db.create_all() creates new tables but never alters existing ones, so we
    add the two new FK columns idempotently."""
    from sqlalchemy import text
    statements = [
        "ALTER TABLE departments ADD COLUMN IF NOT EXISTS hod_user_id INTEGER REFERENCES users(id)",
        "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS teacher_id INTEGER REFERENCES users(id)",
        # Department -> Program -> Batch -> Semester -> Subject hierarchy migration
        "ALTER TABLE programs ADD COLUMN IF NOT EXISTS total_semesters INTEGER",
        "ALTER TABLE subjects ADD COLUMN IF NOT EXISTS semester_id INTEGER REFERENCES semesters(id)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS batch_id INTEGER REFERENCES batches(id)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS semester_id INTEGER REFERENCES semesters(id)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS registration_number VARCHAR(50)",
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS enrollment_status VARCHAR(20) DEFAULT 'active'",
        "ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS batch_id INTEGER REFERENCES batches(id)",
        "ALTER TABLE knowledge_base ADD COLUMN IF NOT EXISTS semester_id INTEGER REFERENCES semesters(id)",
        "ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS batch_id INTEGER REFERENCES batches(id)",
        "ALTER TABLE chat_sessions ADD COLUMN IF NOT EXISTS semester_id INTEGER REFERENCES semesters(id)",
        "ALTER TABLE downloads ADD COLUMN IF NOT EXISTS batch_id INTEGER REFERENCES batches(id)",
        "ALTER TABLE downloads ADD COLUMN IF NOT EXISTS semester_id INTEGER REFERENCES semesters(id)",
        "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS batch_id INTEGER REFERENCES batches(id)",
        "ALTER TABLE notifications ADD COLUMN IF NOT EXISTS semester_id INTEGER REFERENCES semesters(id)",
        # Theme Portal — granular color controls
        "ALTER TABLE theme_settings ADD COLUMN IF NOT EXISTS banner_text_color VARCHAR(20) DEFAULT '#ffffff'",
        "ALTER TABLE theme_settings ADD COLUMN IF NOT EXISTS sidebar_text_color VARCHAR(20) DEFAULT '#ffffff'",
        "ALTER TABLE theme_settings ADD COLUMN IF NOT EXISTS link_color VARCHAR(20)",
    ]
    try:
        with db.engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))
    except Exception:
        # Non-Postgres backends (e.g. SQLite in tests) — create_all already handled schema.
        db.session.rollback()


