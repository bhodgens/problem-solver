"""Wsgi entry point for production deployment"""

from src import create_app
import os

app = create_app(os.environ.get("FLASK_ENV", "prod"))

if __name__ == "__main__":
    app.run()
