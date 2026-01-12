"""
Flask application factory with modular blueprint architecture
"""

from flask import Flask
from flask_login import current_user
from .config import config_by_name
from .extensions import db, migrate, login_manager, oauth, mail


def create_app(config_name="default"):
    """Create and configure Flask application"""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)
    mail.init_app(app)

    # Make mail available in templates
    app.context_processor(lambda: {"mail": mail})

    # Register blueprints
    from .blueprints.auth import auth_bp
    from .blueprints.problems import problems_bp
    from .blueprints.solutions import solutions_bp
    from .blueprints.evaluations import evaluations_bp
    from .blueprints.dashboard import dashboard_bp
    from .blueprints.notifications import notifications_bp
    from .blueprints.api import api_bp

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(problems_bp, url_prefix="/problems")
    app.register_blueprint(solutions_bp, url_prefix="/solutions")
    app.register_blueprint(evaluations_bp, url_prefix="/evaluations")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(api_bp, url_prefix="/api/v1")
    from .blueprints.admin import admin_bp
    from .blueprints.api import api_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(problems_bp, url_prefix="/problems")
    app.register_blueprint(solutions_bp, url_prefix="/solutions")
    app.register_blueprint(evaluations_bp, url_prefix="/evaluations")
    app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(api_bp, url_prefix="/api")

    # Register main routes
    from .blueprints.main import main_bp

    app.register_blueprint(main_bp)

    # Register CLI commands
    from .cli import register_cli

    register_cli(app)

    # Configure OAuth
    configure_oauth(app)

    # Template context
    @app.context_processor
    def inject_user():
        return {"current_user": current_user}

    # Error handlers
    register_error_handlers(app)

    return app


def configure_oauth(app):
    """Configure OAuth providers"""
    if app.config.get("GOOGLE_CLIENT_ID"):
        oauth.register(
            "google",
            client_id=app.config["GOOGLE_CLIENT_ID"],
            client_secret=app.config["GOOGLE_CLIENT_SECRET"],
            authorize_url="https://accounts.google.com/o/oauth2/auth",
            authorize_params=None,
            access_token_url="https://oauth2.googleapis.com/token",
            access_token_params=None,
            refresh_token_url=None,
            client_kwargs={"scope": "openid email profile"},
        )


def register_error_handlers(app):
    """Register application error handlers"""
    from flask import render_template

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403
