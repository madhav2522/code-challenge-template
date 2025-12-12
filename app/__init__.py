"""
Application factory.
Creates Flask app, initializes extensions, registers blueprints,
and ensures DB tables are created.
"""

from flask import Flask
from flasgger import Swagger
from .config import Config
from .database import db

def create_app(config_object=None):
    app = Flask(__name__, instance_relative_config=False)

    # Use provided config (for tests) or default
    if config_object:
        app.config.from_object(config_object)
    else:
        app.config.from_object(Config)

    db.init_app(app)
    Swagger(app)

    from .routes import api
    app.register_blueprint(api, url_prefix="/api")

    # Create tables
    with app.app_context():
        db.create_all()

    return app

