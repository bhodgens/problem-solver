"""
Updated main entry point for Flask application factory
"""

import os
from src import create_app

if __name__ == "__main__":
    config_name = os.environ.get("FLASK_ENV", "dev")
    app = create_app(config_name)
    app.run(host="0.0.0.0", port=8000, debug=config_name == "dev")
