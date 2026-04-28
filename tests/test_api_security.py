from types import SimpleNamespace

from app import create_app
from app.extensions import db


def _build_client_with_csrf():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "RATELIMIT_ENABLED": False,
            "GOOGLE_MAPS_API_KEY": "test-key",
            "API_AUTH_TOKEN": "csrf-test-token",
            "API_REQUIRE_CSRF": False,
        }
    )
    with app.app_context():
        db.drop_all()
        db.create_all()
    return app, app.test_client()


def test_api_post_is_csrf_exempt_but_requires_api_token(monkeypatch):
    app, client = _build_client_with_csrf()

    def fake_start_search_job(
        flask_app, keyword, cities, target_count=1000, radius=None
    ):
        assert flask_app is app
        assert keyword == "Elektriker"
        assert cities == ["Köln"]
        return SimpleNamespace(id=42, status="queued")

    monkeypatch.setattr("app.routes.api.start_search_job", fake_start_search_job)

    # Kein CSRF-Token, aber gültiger API-Token -> erlaubt
    ok_response = client.post(
        "/api/search/start",
        json={"keyword": "Elektriker", "cities": "Köln"},
        headers={"X-API-Key": app.config["API_AUTH_TOKEN"]},
    )
    assert ok_response.status_code == 202

    # Kein API-Token -> abgelehnt
    denied_response = client.post(
        "/api/search/start",
        json={"keyword": "Elektriker", "cities": "Köln"},
    )
    assert denied_response.status_code == 401
    assert denied_response.get_json() == {"error": "unauthorized"}
