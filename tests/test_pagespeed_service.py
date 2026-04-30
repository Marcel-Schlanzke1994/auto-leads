from types import SimpleNamespace

import requests

from app.services.pagespeed_service import analyze_pagespeed
from app.services.website_fetcher import FetchResult


class DummyResponse:
    def __init__(self, payload: dict | None = None, status_code: int = 200) -> None:
        self.payload = payload or {}
        self.status_code = status_code

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise requests.HTTPError(
                response=SimpleNamespace(status_code=self.status_code)
            )

    def json(self) -> dict:
        return self.payload


def _fetch_result() -> FetchResult:
    return FetchResult(
        requested_url="https://example.com",
        normalized_url="https://example.com",
        url="https://example.com",
        body="<html><body>ok</body></html>",
        status_code=200,
        page_load_ms=800,
        redirect_history=[],
        used_https=True,
    )


def test_pagespeed_fallback_has_error_metadata_and_warning_log(
    app, monkeypatch, caplog
):
    with app.app_context():
        app.config["PAGESPEED_API_KEY"] = "test-key"
        app.config["PAGESPEED_MAX_RETRIES"] = 2
        policy = app.config["EXTERNAL_SERVICE_POLICIES"]["pagespeed"]

        def _always_bad_request(*args, **kwargs):
            return DummyResponse(status_code=400)

        monkeypatch.setattr(
            "app.services.pagespeed_service.requests.get", _always_bad_request
        )

        result = analyze_pagespeed("https://example.com", _fetch_result(), timeout=2.0)

    assert result["source"] == "heuristic_fallback"
    assert result["error_code"] == "HTTP_400"
    assert result["error_message"] == "PageSpeed API returned HTTP 400"
    assert result["fallback_reason"] == "pagespeed_request_failed_non_transient"
    assert "PageSpeed fallback activated for url=https://example.com" in caplog.text
    assert f"timeout={policy.timeout:.2f}s" in caplog.text


def test_pagespeed_retries_transient_timeout_then_returns_api_payload(app, monkeypatch):
    payload = {
        "lighthouseResult": {
            "categories": {"performance": {"score": 0.9}, "seo": {"score": 0.7}},
            "audits": {"first-contentful-paint": {"numericValue": 321.5}},
        }
    }
    calls = {"count": 0}

    def _timeout_then_success(*args, **kwargs):
        calls["count"] += 1
        if calls["count"] == 1:
            raise requests.Timeout("deadline")
        return DummyResponse(payload=payload)

    monkeypatch.setattr(
        "app.services.pagespeed_service.requests.get", _timeout_then_success
    )
    monkeypatch.setattr("app.services.pagespeed_service.time.sleep", lambda _: None)

    with app.app_context():
        app.config["PAGESPEED_API_KEY"] = "test-key"
        app.config["PAGESPEED_MAX_RETRIES"] = 1
        result = analyze_pagespeed("https://example.com", _fetch_result(), timeout=2.0)

    assert calls["count"] == 2
    assert result["source"] == "psi_api"
    assert result["performance_score"] == 90.0
    assert result["error_code"] is None
    assert result["fallback_reason"] is None


def test_pagespeed_fallback_after_transient_retry_exhausted(app, monkeypatch):
    calls = {"count": 0}

    def _always_timeout(*args, **kwargs):
        calls["count"] += 1
        raise requests.Timeout("deadline")

    monkeypatch.setattr("app.services.pagespeed_service.requests.get", _always_timeout)
    monkeypatch.setattr("app.services.pagespeed_service.time.sleep", lambda _: None)

    with app.app_context():
        app.config["PAGESPEED_API_KEY"] = "test-key"
        app.config["PAGESPEED_MAX_RETRIES"] = 1
        result = analyze_pagespeed("https://example.com", _fetch_result(), timeout=2.0)

    assert calls["count"] == 2
    assert result["source"] == "heuristic_fallback"
    assert result["error_code"] == "TIMEOUT"
    assert result["fallback_reason"] == "pagespeed_request_failed_after_retries"
