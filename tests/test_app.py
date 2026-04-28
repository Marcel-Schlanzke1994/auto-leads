from types import SimpleNamespace

from app.extensions import db
from app.models import Lead, SearchJob
from app.services.duplicate_service import is_duplicate
from app.services.lead_score_service import calculate_lead_score
from app.services.search_runner_service import (
    _create_places_client,
    _extract_city,
    _run_search_job,
)
from app.utils import (
    is_private_hostname,
    normalize_website_url,
    parse_float,
    parse_int,
)


def test_env_driven_config(app):
    assert app.config["PLACES_PROVIDER"] == "google_places"
    assert app.config["REQUEST_TIMEOUT"] == 8.0


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
                normalized_company_name="muster",
                source_query="x",
                city="Köln",
                city_normalized="köln",
                website="https://firma.de",
                domain="firma.de",
                phone="+49 1234",
                phone_normalized="+491234",
                email="x@firma.de",
                email_normalized="x@firma.de",
                google_place_id="abc",
            )
        )
        db.session.commit()

        assert is_duplicate(
            place_id="abc",
            company_name="Andere",
            city=None,
            website=None,
            phone=None,
            email=None,
        )
        assert is_duplicate(
            place_id=None,
            company_name="Neu",
            city=None,
            website="https://firma.de/kontakt",
            phone=None,
            email=None,
        )
        assert not is_duplicate(
            place_id=None,
            company_name="MUSTER GMBH",
            city=None,
            website=None,
            phone=None,
            email=None,
        )
        assert is_duplicate(
            place_id=None,
            company_name="neu name",
            city=None,
            website=None,
            phone="+491234",
            email=None,
        )


def test_city_extraction_prefers_structured_components():
    city = _extract_city(
        [
            {"types": ["postal_code"], "longText": "50667"},
            {"types": ["locality"], "longText": "Köln"},
        ],
        "Domkloster 4, 50667 Köln, Deutschland",
    )
    assert city == "Köln"


def test_city_extraction_fallback_avoids_postal_code():
    city = _extract_city([], "Musterstraße 1, 50667 Köln, Deutschland")
    assert city == "Köln"


def test_score_calculation_contains_reasons(app):
    with app.app_context():
        lead = Lead(company_name="Score GmbH", source_query="q")
        score, reasons = calculate_lead_score(lead)
    assert score > 0
    assert any("REVIEW_COUNT_LOW" in item for item in reasons)


def test_lead_creation_and_dashboard(client, app):
    with app.app_context():
        db.session.add(
            Lead(
                company_name="Test GmbH",
                source_query="roof cologne",
                score=42,
                google_rating=3.9,
                review_count=12,
            )
        )
        db.session.commit()

    resp = client.get("/")
    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Test GmbH" in body
    assert "Mit Google Rating" in body


def test_lead_detail_shows_rating_and_reviews(client, app):
    with app.app_context():
        lead = Lead(
            company_name="Detail GmbH",
            source_query="x",
            google_rating=4.5,
            review_count=91,
        )
        db.session.add(lead)
        db.session.commit()
        lead_id = lead.id

    resp = client.get(f"/lead/{lead_id}")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "Google Sterne" in text
    assert "91" in text


def test_api_endpoints(client, app):
    with app.app_context():
        lead = Lead(company_name="API GmbH", source_query="query")
        db.session.add(lead)
        db.session.add(
            SearchJob(
                keyword="Dachdecker",
                cities="Köln",
                status="running",
                target_count=1000,
                total_found_raw=10,
                total_processed=1,
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
    payload = progress_resp.get_json()
    assert "status" in payload
    assert "total_found_raw" in payload


def test_api_search_start_with_target_count(client, app, monkeypatch):
    def fake_start_search_job(
        flask_app, keyword, cities, target_count=1000, radius=None
    ):
        assert flask_app is app
        assert keyword == "Elektriker"
        assert cities == ["Köln", "Bonn"]
        assert target_count == 777
        return SimpleNamespace(id=123, status="queued")

    monkeypatch.setattr("app.routes.api.start_search_job", fake_start_search_job)
    response = client.post(
        "/api/search/start",
        json={"keyword": "Elektriker", "cities": "Köln, Bonn", "target_count": 777},
    )

    assert response.status_code == 202
    payload = response.get_json()
    assert payload["job_id"] == 123
    assert payload["status"] == "queued"


def test_api_search_start_with_invalid_target_count_returns_400(client):
    response = client.post(
        "/api/search/start",
        json={"keyword": "Elektriker", "cities": "Köln", "target_count": "abc"},
    )

    assert response.status_code == 400
    assert response.get_json() == {"error": "target_count must be an integer"}


def test_api_search_start_with_negative_target_count_clamps_to_minimum(
    client, app, monkeypatch
):
    def fake_start_search_job(
        flask_app, keyword, cities, target_count=1000, radius=None
    ):
        assert flask_app is app
        assert keyword == "Elektriker"
        assert cities == ["Köln"]
        assert target_count == 1
        return SimpleNamespace(id=124, status="queued")

    monkeypatch.setattr("app.routes.api.start_search_job", fake_start_search_job)
    response = client.post(
        "/api/search/start",
        json={"keyword": "Elektriker", "cities": "Köln", "target_count": -5},
    )

    assert response.status_code == 202
    payload = response.get_json()
    assert payload["job_id"] == 124
    assert payload["status"] == "queued"
    assert payload["target_count"] == 1


def test_csv_export_contains_new_fields(client, app):
    with app.app_context():
        db.session.add(
            Lead(
                company_name="CSV GmbH",
                source_query="q",
                google_rating=4.1,
                review_count=5,
                score_reasons="A\nB",
            )
        )
        db.session.commit()

    resp = client.get("/export/csv")
    assert resp.status_code == 200
    text = resp.get_data(as_text=True)
    assert "google_rating" in text
    assert "review_count" in text
    assert "score_reasons" in text


def test_google_provider_requires_api_key(app):
    app.config.update(PLACES_PROVIDER="google_places", GOOGLE_MAPS_API_KEY="")

    with app.app_context():
        client, source, error = _create_places_client(app)

    assert client is None
    assert source == "google_places"
    assert error == "GOOGLE_MAPS_API_KEY fehlt"


def test_google_provider_is_activated(app):
    app.config.update(PLACES_PROVIDER="google_places", GOOGLE_MAPS_API_KEY="abc")

    with app.app_context():
        client, source, error = _create_places_client(app)

    assert client is not None
    assert source == "google_places"
    assert error is None


def test_search_job_reaches_target_and_paginates(app, monkeypatch):
    with app.app_context():
        job = SearchJob(keyword="Dachdecker", cities="Köln", target_count=3)
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    class FakePlace:
        def __init__(self, idx: int):
            self.place_id = f"p{idx}"
            self.display_name = f"Firma {idx}"
            self.formatted_address = f"Straße {idx}, Köln, Deutschland"
            self.address_components = [{"types": ["locality"], "longText": "Köln"}]
            self.website = f"https://firma{idx}.de"
            self.phone = f"+49 100{idx}"
            self.rating = 4.0
            self.review_count = 10
            self.primary_type = "roofing_contractor"
            self.all_types = ["roofing_contractor", "establishment"]

    class FakeClient:
        def text_search_paginated(self, query, max_results, safety_page_limit):
            return SimpleNamespace(
                place_ids=["p1", "p2", "p3", "p4"], total_found_raw=4
            )

        def place_details(self, place_id):
            idx = int(place_id.replace("p", ""))
            return FakePlace(idx)

    monkeypatch.setattr(
        "app.services.search_runner_service._create_places_client",
        lambda _app: (FakeClient(), "google_places", None),
    )
    monkeypatch.setattr(
        "app.services.search_runner_service.audit_website",
        lambda website, timeout: SimpleNamespace(
            site_title="T",
            meta_description="D",
            has_h1=True,
            has_cta=True,
            mobile_signals=True,
            has_contact_info=True,
            page_load_ms=100,
            impressum_found=True,
            audit_notes="ok",
            parser_notes="ok",
            checked_pages="/",
            email="x@example.com",
            phone=None,
            owner_name="Owner",
            legal_form="GmbH",
            critical_issues=[],
            warnings=[],
            opportunities=[],
            quick_wins=[],
            top_sales_arguments=["arg"],
            raw_pagespeed={
                "performance_score": 80,
                "accessibility_score": 80,
                "best_practices_score": 80,
                "seo_score": 80,
                "lcp_ms": 1000,
                "fcp_ms": 400,
                "ttfb_ms": 100,
            },
        ),
    )

    _run_search_job(app, job_id, "Dachdecker", ["Köln"])

    with app.app_context():
        updated = db.session.get(SearchJob, job_id)
        assert updated.status == "finished"
        assert updated.total_created == 3
        assert updated.total_found_raw == 4
        assert Lead.query.count() == 3


def test_job_detail_and_progress_endpoints(client, app):
    with app.app_context():
        job = SearchJob(
            keyword="Maler",
            cities="Berlin",
            status="running",
            target_count=1500,
            total_found_raw=50,
            total_created=12,
            duplicates_skipped=3,
            errors=1,
            log_json=[{"phase": "start", "timestamp": "2026-01-01T00:00:00Z"}],
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    detail_resp = client.get(f"/jobs/{job_id}/json")
    assert detail_resp.status_code == 200
    detail_payload = detail_resp.get_json()
    assert detail_payload["events_count"] == 1

    poll_resp = client.get(f"/jobs/{job_id}/progress?since=0")
    assert poll_resp.status_code == 200
    poll_payload = poll_resp.get_json()
    assert poll_payload["events_total"] == 1
    assert poll_payload["target_count"] == 1000


def test_api_progress_supports_since(client, app):
    with app.app_context():
        job = SearchJob(
            keyword="Fensterbauer",
            cities="Hamburg",
            status="running",
            log_json=[
                {"phase": "start", "timestamp": "2026-01-01T00:00:00Z"},
                {"phase": "city_start", "timestamp": "2026-01-01T00:01:00Z"},
            ],
        )
        db.session.add(job)
        db.session.commit()
        job_id = job.id

    resp = client.get(f"/api/search/progress?job_id={job_id}&since=1")
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload["events_total"] == 2
    assert len(payload["events"]) == 1
