"""
Flask extensions initialization - decoupled from app creation
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from authlib.integrations.flask_client import OAuth
from flask_mail import Mail
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for SQLAlchemy models"""

    pass


# Initialize extensions without binding to app
db = SQLAlchemy(model_class=Base)
migrate = Migrate()
login_manager = LoginManager()
oauth = OAuth()
mail = Mail()


@login_manager.user_loader
def load_user(user_id):
    """User loader for Flask-Login"""
    from .models.user import User

    return User.query.get(int(user_id))
