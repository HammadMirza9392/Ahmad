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
    import app.models.classes
    import app.models.batch
    import app.models.semester
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
    import app.models.enrollment
    import app.models.quiz
    import app.models.theme
    import app.models.study_material
    import app.models.announcement
    import app.models.assignment
    db.create_all()
    _ensure_new_columns()
    _migrate_class_to_batch_semester()


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


def _migrate_class_to_batch_semester():
    """One-time data migration: old flat Class model -> Batch/Semester hierarchy.

    Best-effort and non-destructive:
    - Old `classes` / `class_subjects` tables are left untouched in the DB
      (nothing drops them); code simply stops reading from them after this runs.
    - For every Program, creates ONE Batch (best-effort inference: no reliable
      start/end year existed on the old Class model, so start_year/end_year are
      left NULL for the admin to fill in manually; status defaults to 'active').
    - For every Class under that program, creates a corresponding Semester under
      the new Batch, trying to parse a leading integer out of the class's
      year/name for `number`, else falling back to sequential 1, 2, 3...
    - Subjects linked to a class via the old ClassSubject bridge get
      `semester_id` set to the first linked semester. If a subject had multiple
      class links (possible, if unlikely, under the old schema), a warning is
      printed since the new schema only supports one semester per subject.
    - Students with a class_id get batch_id/semester_id set from the mapping.

    Guarded to run once: skips entirely if any Batch rows already exist.
    Wrapped in try/except so a migration failure never blocks app startup.
    """
    import re
    from sqlalchemy import text
    from app.models.program import Program
    from app.models.batch import Batch
    from app.models.semester import Semester
    from app.models.classes import Class, ClassSubject
    from app.models.subject import Subject
    from app.models.user import User

    try:
        if Batch.query.first() is not None:
            return  # already migrated (or fresh install with no legacy data)

        old_classes = Class.query.all()
        if not old_classes:
            return  # nothing to migrate

        class_to_semester = {}  # old Class.id -> new Semester

        for program in Program.query.all():
            program_classes = [c for c in old_classes if c.program_id == program.id]
            if not program_classes:
                continue

            batch = Batch(
                name=f'{program.name} Batch',
                slug=f'{program.slug}-batch-1',
                start_year=None,  # best-effort: old schema had no reliable start year
                end_year=None,
                status='active',
                program_id=program.id,
                is_active=True,
            )
            db.session.add(batch)
            db.session.flush()

            for idx, cls in enumerate(sorted(program_classes, key=lambda c: c.sort_order or 0), start=1):
                number = None
                for source in (cls.year, cls.name):
                    if source:
                        match = re.search(r'\d+', source)
                        if match:
                            number = int(match.group())
                            break
                if number is None:
                    number = idx

                semester = Semester(
                    name=cls.name,
                    slug=cls.slug or f'{batch.slug}-sem-{idx}',
                    number=number,
                    batch_id=batch.id,
                    is_active=cls.is_active,
                    sort_order=cls.sort_order or 0,
                )
                db.session.add(semester)
                db.session.flush()
                class_to_semester[cls.id] = semester

        db.session.commit()

        # Migrate ClassSubject bridge -> Subject.semester_id (first link wins)
        subject_class_counts = {}
        for cs in ClassSubject.query.all():
            subject_class_counts.setdefault(cs.subject_id, []).append(cs.class_id)

        for subject_id, class_ids in subject_class_counts.items():
            if len(class_ids) > 1:
                print(f'[migration] WARNING: Subject {subject_id} was linked to multiple '
                      f'classes ({class_ids}); migrated to the first one only. Please review manually.')
            first_class_id = class_ids[0]
            semester = class_to_semester.get(first_class_id)
            if semester:
                subject = db.session.get(Subject, subject_id)
                if subject and not subject.semester_id:
                    subject.semester_id = semester.id

        # Migrate students. User.class_id is no longer a mapped attribute (the
        # model dropped it in favor of batch_id/semester_id), but the raw column
        # still exists in the DB, so read it with raw SQL rather than the ORM.
        rows = db.session.execute(text('SELECT id, class_id FROM users WHERE class_id IS NOT NULL')).fetchall()
        for row in rows:
            semester = class_to_semester.get(row.class_id)
            if semester:
                user = db.session.get(User, row.id)
                if user:
                    user.batch_id = semester.batch_id
                    user.semester_id = semester.id

        db.session.commit()
        print(f'[migration] Migrated {len(class_to_semester)} classes into batches/semesters.')

    except Exception as e:
        db.session.rollback()
        import logging
        logging.getLogger(__name__).warning(f'Class->Batch/Semester migration failed (non-fatal): {e}')
