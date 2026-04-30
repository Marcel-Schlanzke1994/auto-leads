from app.services.web_perf import analyze_web_perf
from app.services.website_fetcher import FetchResult


def _fetch(html: str, headers: dict[str, str]) -> FetchResult:
    return FetchResult(
        requested_url="https://example.com",
        normalized_url="https://example.com",
        url="https://example.com",
        body=html,
        status_code=200,
        page_load_ms=900,
        redirect_history=[],
        used_https=True,
        response_headers=headers,
    )


def test_web_perf_analyzer_with_minimal_html():
    result = analyze_web_perf(
        _fetch("<html><head></head><body>ok</body></html>", {}), {}
    )
    assert result.source in {"mixed", "local"}
    assert result.mobile_performance_risk == "high"


def test_web_perf_recognizes_compression_and_cache_headers():
    result = analyze_web_perf(
        _fetch(
            (
                "<html><head><meta name='viewport' content='width=device-width'>"
                "</head><body></body></html>"
            ),
            {"content-encoding": "br", "cache-control": "public, max-age=3600"},
        ),
        {},
    )
    assert result.uses_compression is True
    assert result.cache_policy_present is True


def test_web_perf_missing_pagespeed_fields_does_not_crash():
    result = analyze_web_perf(
        _fetch("<html><body></body></html>", {}), {"source": "psi_api"}
    )
    assert result.performance_score is None
    assert isinstance(result.recommendations, list)
