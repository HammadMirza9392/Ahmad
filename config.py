"""
Application Configuration
Manages all environment-specific settings for the LMS application.
"""
import os
from datetime import timedelta
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration shared across all environments."""

    # Flask Core
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')

    # Supabase PostgreSQL
    SUPABASE_URL = os.getenv('SUPABASE_URL', '')
    SUPABASE_KEY = os.getenv('SUPABASE_KEY', '')
    SUPABASE_DB_HOST = os.getenv('SUPABASE_DB_HOST', '')
    SUPABASE_DB_PORT = os.getenv('SUPABASE_DB_PORT', '5432')
    SUPABASE_DB_NAME = os.getenv('SUPABASE_DB_NAME', 'postgres')
    SUPABASE_DB_USER = os.getenv('SUPABASE_DB_USER', 'postgres')
    SUPABASE_DB_PASSWORD = os.getenv('SUPABASE_DB_PASSWORD', '')

    # URL-encode password to handle special characters like @, !, #
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg://{quote_plus(os.getenv('SUPABASE_DB_USER', 'postgres'))}:"
        f"{quote_plus(os.getenv('SUPABASE_DB_PASSWORD', ''))}@"
        f"{os.getenv('SUPABASE_DB_HOST', 'localhost')}:"
        f"{os.getenv('SUPABASE_DB_PORT', '5432')}/"
        f"{os.getenv('SUPABASE_DB_NAME', 'postgres')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 300,
        'pool_pre_ping': True,
        'max_overflow': 20,
    }

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Upload
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app', 'static', 'uploads')
    ALLOWED_EXTENSIONS = {
        'images': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'},
        'documents': {'pdf', 'doc', 'docx', 'txt', 'md', 'csv', 'xlsx', 'xls', 'ppt', 'pptx'},
        'all': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg', 'pdf', 'doc', 'docx',
                'txt', 'md', 'csv', 'xlsx', 'xls', 'ppt', 'pptx'},
    }

    # Rate Limiting
    RATELIMIT_DEFAULT = "200 per hour"
    RATELIMIT_STORAGE_URI = "memory://"

    # Encryption key for API keys stored in DB
    ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', '')

    # Mail (for password reset)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', '')


class DevelopmentConfig(Config):
    """Development-specific overrides."""
    DEBUG = True
    SESSION_COOKIE_SECURE = False


class ProductionConfig(Config):
    """Production-specific overrides."""
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    PREFERRED_URL_SCHEME = 'https'


class TestingConfig(Config):
    """Testing-specific overrides."""
    TESTING = True
    WTF_CSRF_ENABLED = False


config_map = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}
