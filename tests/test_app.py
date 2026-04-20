from auto_leads.extensions import db
from auto_leads.models import Lead, SearchJob
from auto_leads.services.dedupe import is_duplicate_candidate
from auto_leads.utils import (
    is_private_hostname,
    normalize_website_url,
    parse_float,
    parse_int,
)


def test_url_normalization():
    assert normalize_website_url("example.com") == "https://example.com"
    assert normalize_website_url("https://example.com") == "https://example.com"
    assert normalize_website_url("ftp://example.com") is None


def test_private_host_guard():
    assert is_private_hostname("localhost") is True
    assert is_private_hostname("127.0.0.1") is True


def test_number_parsers():
    assert parse_float("4,4") == 4.4
    assert parse_float("abc") is None
    assert parse_int("1.234") == 1234
    assert parse_int(None) is None


def test_duplicate_filter(app):
    with app.app_context():
        db.session.add(
            Lead(
                company_name="Muster GmbH",
                source_query="x",
                website="https://firma.de",
                phone="+491234",
                email="x@firma.de",
                google_place_id="abc",
            )
        )
        db.session.commit()

        assert is_duplicate_candidate(
            place_id="abc",
            company_name="Andere",
            website=None,
            phone=None,
            email=None,
        )
        assert is_duplicate_candidate(
            place_id=None,
            company_name="Neu",
            website="https://firma.de/kontakt",
            phone=None,
            email=None,
        )


def test_lead_creation_and_dashboard(client, app):
    with app.app_context():
        db.session.add(
            Lead(company_name="Test GmbH", source_query="roof cologne", score=42)
        )
        db.session.commit()

    resp = client.get("/")
    assert resp.status_code == 200
    assert "Test GmbH" in resp.get_data(as_text=True)


def test_api_endpoints(client, app):
    with app.app_context():
        lead = Lead(company_name="API GmbH", source_query="query")
        db.session.add(lead)
        db.session.add(
            SearchJob(
                keyword="Dachdecker",
                cities="Köln",
                status="running",
                total=10,
                processed=1,
            )
        )
        db.session.commit()
        lead_id = lead.id

    list_resp = client.get("/api/leads")
    assert list_resp.status_code == 200
    assert isinstance(list_resp.get_json(), list)

    detail_resp = client.get(f"/api/leads/{lead_id}")
    assert detail_resp.status_code == 200

    progress_resp = client.get("/api/search/progress")
    assert progress_resp.status_code == 200
    assert "status" in progress_resp.get_json()


def test_csv_export(client, app):
    with app.app_context():
        db.session.add(Lead(company_name="CSV GmbH", source_query="q"))
        db.session.commit()

    resp = client.get("/export/csv")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "company_name" in text
    assert "CSV GmbH" in text
