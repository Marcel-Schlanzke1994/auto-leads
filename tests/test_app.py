import pytest

from app import (
    Lead,
    _is_private_hostname,
    _normalize_website_url,
    _to_float,
    _to_int,
    audit_website,
    create_app,
    db,
)


def test_parsers_handle_common_inputs():
    assert _to_float("4,5") == 4.5
    assert _to_float("abc") is None
    assert _to_int("1.234") == 1234
    assert _to_int(None) is None


def test_url_normalization_and_host_protection():
    assert _normalize_website_url("example.com") == "https://example.com"
    assert _normalize_website_url("https://example.com") == "https://example.com"
    assert _normalize_website_url("ftp://example.com") is None

    assert _is_private_hostname("localhost") is True
    assert _is_private_hostname("127.0.0.1") is True
    assert _is_private_hostname("example.com") is False

    with pytest.raises(ValueError):
        audit_website("http://127.0.0.1", timeout=1)


def test_dashboard_and_api_endpoints():
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,
        }
    )

    with app.app_context():
        db.drop_all()
        db.create_all()
        lead = Lead(company_name="Test GmbH", source="test", score=55)
        db.session.add(lead)
        db.session.commit()
        lead_id = lead.id

    client = app.test_client()
    dashboard = client.get("/")
    assert dashboard.status_code == 200
    assert "Test GmbH" in dashboard.get_data(as_text=True)

    api_list = client.get("/api/leads")
    assert api_list.status_code == 200
    data = api_list.get_json()
    assert isinstance(data, list)
    assert data[0]["company_name"] == "Test GmbH"

    api_detail = client.get(f"/api/leads/{lead_id}")
    assert api_detail.status_code == 200
    assert api_detail.get_json()["id"] == lead_id

    missing = client.get("/api/leads/9999")
    assert missing.status_code == 404
