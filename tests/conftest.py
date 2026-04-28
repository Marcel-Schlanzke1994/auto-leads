import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pytest

from app import create_app  # noqa: E402
from app.extensions import db  # noqa: E402


@pytest.fixture()
def app():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "RATELIMIT_ENABLED": False,
            "GOOGLE_MAPS_API_KEY": "test-key",
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()
