
import os
import tempfile
import pytest
from app import create_app
from app.config import TestConfig
from app.database import db

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = create_app(TestConfig)
    # ensure fresh db
    with app.app_context():
        db.create_all()
    yield app
    # teardown: drop db
    with app.app_context():
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def tmp_wx_folder(tmp_path):
    """
    Create a temporary wx_data folder containing one small sample file.
    Example line format:
        19850101\t215\t105\t5
    (values in tenths; -9999 for missing)
    """
    folder = tmp_path / "wx_data"
    folder.mkdir()
    file_path = folder / "STATION_TEST.txt"
    content = "\n".join([
        "19850101\t215\t105\t5",    # 21.5,10.5,0.5mm
        "19850102\t-9999\t95\t0",   # missing max, 9.5,0.0mm
        "19850103\t200\t-9999\t10"  # 20.0, missing min,1.0mm
    ])
    file_path.write_text(content)
    return str(folder)

