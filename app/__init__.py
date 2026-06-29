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

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(student_bp, url_prefix='/student')
    app.register_blueprint(cms_bp)
    app.register_blueprint(api_bp, url_prefix='/api')

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
        return dict(
            institution=institution,
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
    import app.models.classes
    import app.models.subject
    import app.models.knowledge_base
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
    db.create_all()
