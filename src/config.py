"""
Configuration classes for different environments
"""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key-change-in-production"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # OAuth configuration
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")

    # Email configuration
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", "587"))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() in ["true", "on", "1"]
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

    # Application settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    POSTS_PER_PAGE = 20

    # Security
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Anonymity settings
    ANONYMITY_ENABLED = True
    ANONYMITY_DECAY_DAYS = 30

    # Notifications
    NOTIFICATIONS_ENABLED = True
    DAILY_DIGEST_ENABLED = True

    # API settings
    API_ENABLED = True
    API_RATE_LIMIT = 100

    # Admin emails
    ADMIN_EMAILS = (
        os.environ.get("ADMIN_EMAILS", "").split(",")
        if os.environ.get("ADMIN_EMAILS")
        else []
    )


class DevelopmentConfig(Config):
    """Development configuration"""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DEV_DATABASE_URL") or "sqlite:///problem_solver_dev.db"
    )
    SESSION_COOKIE_SECURE = False


class TestingConfig(Config):
    """Testing configuration"""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("TEST_DATABASE_URL") or "sqlite:///:memory:"
    )
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = (
        os.environ.get("DATABASE_URL") or "sqlite:///problem_solver.db"
    )
    SESSION_COOKIE_SECURE = True

    # Production security headers
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True


config_by_name = {
    "dev": DevelopmentConfig,
    "test": TestingConfig,
    "prod": ProductionConfig,
    "default": DevelopmentConfig,
}
