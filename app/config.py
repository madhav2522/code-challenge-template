"""Configuration for the Flask app."""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    # Default: use local SQLite file in project root
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///weather.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flasgger metadata
    SWAGGER = {
        "title": "CTVA Weather API",
        "uiversion": 3
    }

class TestConfig(Config):
    # Fast ephemeral SQLite DB for tests (in-memory)
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True

