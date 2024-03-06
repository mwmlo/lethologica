import os
import secrets

from dotenv import load_dotenv
from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect

from .views import home_page

csrf = CSRFProtect()


def create_app(enable_limits=True, csrf_enabled=True):
    app = Flask(__name__, static_url_path="/static", instance_relative_config=True)
    # Security
    load_dotenv()
    app.secret_key = os.getenv("APP_SECRET")
    csrf.init_app(app)
    app.config["WTF_CSRF_ENABLED"] = csrf_enabled
    # Default rate limits
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["500 per day", "100 per hour", "5 per second"],
    )
    limiter.enabled = enable_limits
    app.register_blueprint(home_page)
    return app


app = create_app()
