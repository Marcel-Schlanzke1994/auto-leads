from __future__ import annotations

import logging
import os
import time

import requests
from flask import current_app, has_app_context

from app.services.website_fetcher import FetchResult


PSI_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PSI_API_KEY = os.getenv("PAGESPEED_API_KEY", "").strip()
DEFAULT_MAX_RETRIES = 1


def extract_page_load_ms(fetch_result: FetchResult) -> int:
    return fetch_result.page_load_ms


def analyze_pagespeed(url: str, fetch_result: FetchResult, timeout: float) -> dict:
    psi_api_key = PSI_API_KEY
    request_timeout = timeout
    request_delay = 0.0
    max_retries = DEFAULT_MAX_RETRIES
    if has_app_context():
        psi_api_key = current_app.config.get("PAGESPEED_API_KEY", "").strip()
        policy = current_app.config["EXTERNAL_SERVICE_POLICIES"]["pagespeed"]
        request_timeout = policy.timeout
        request_delay = policy.min_interval_seconds
        max_retries = max(0, int(current_app.config.get("PAGESPEED_MAX_RETRIES", 1)))
    if psi_api_key:
        last_error: requests.RequestException | None = None
        retry_count = 0
        max_attempts = max_retries + 1
        for attempt_index in range(max_attempts):
            if request_delay > 0:
                time.sleep(request_delay)
            try:
                response = requests.get(
                    PSI_API_URL,
                    timeout=request_timeout,
                    params={"url": url, "strategy": "mobile", "key": psi_api_key},
                )
                response.raise_for_status()
                payload = response.json()
                lighthouse = payload.get("lighthouseResult") or {}
                categories = lighthouse.get("categories") or {}
                audits = lighthouse.get("audits") or {}
                return {
                    "source": "psi_api",
                    "performance_score": _score(categories, "performance"),
                    "seo_score": _score(categories, "seo"),
                    "accessibility_score": _score(categories, "accessibility"),
                    "best_practices_score": _score(categories, "best-practices"),
                    "fcp_ms": _numeric_audit(audits, "first-contentful-paint"),
                    "lcp_ms": _numeric_audit(audits, "largest-contentful-paint"),
                    "ttfb_ms": _numeric_audit(audits, "server-response-time"),
                    "raw": payload,
                    "error_code": None,
                    "error_message": None,
                    "fallback_reason": None,
                }
            except requests.RequestException as exc:
                last_error = exc
                if not _is_transient_pagespeed_error(exc):
                    break
                if attempt_index >= max_attempts - 1:
                    break
                retry_count += 1

        if last_error is not None:
            error_code, error_message = _error_diagnostics(last_error)
            fallback_reason = (
                "pagespeed_request_failed_after_retries"
                if _is_transient_pagespeed_error(last_error) and retry_count > 0
                else "pagespeed_request_failed_non_transient"
            )
            _log_pagespeed_fallback(
                url=url,
                error=last_error,
                timeout=request_timeout,
                min_interval_seconds=request_delay,
                retries=max_retries,
                retry_count=retry_count,
            )
            return _heuristic_fallback(
                fetch_result=fetch_result,
                error_code=error_code,
                error_message=error_message,
                fallback_reason=fallback_reason,
            )

    return _heuristic_fallback(
        fetch_result=fetch_result,
        error_code="PAGESPEED_API_KEY_MISSING",
        error_message="PAGESPEED_API_KEY is not configured",
        fallback_reason="pagespeed_api_disabled",
    )


def _score(categories: dict, key: str) -> float | None:
    entry = categories.get(key) or {}
    score = entry.get("score")
    if score is None:
        return None
    return round(float(score) * 100, 1)


def _numeric_audit(audits: dict, key: str) -> int | None:
    entry = audits.get(key) or {}
    value = entry.get("numericValue")
    if value is None:
        return None
    return int(value)


def _heuristic_fallback(
    fetch_result: FetchResult,
    error_code: str | None,
    error_message: str | None,
    fallback_reason: str,
) -> dict:
    page_size_kb = len((fetch_result.body or "").encode("utf-8")) / 1024
    estimated_perf = max(
        5.0, min(99.0, 100 - (fetch_result.page_load_ms / 80) - (page_size_kb / 40))
    )
    return {
        "source": "heuristic_fallback",
        "performance_score": round(estimated_perf, 1),
        "seo_score": 60.0,
        "accessibility_score": 60.0,
        "best_practices_score": 65.0,
        "fcp_ms": int(fetch_result.page_load_ms * 0.6),
        "lcp_ms": int(fetch_result.page_load_ms * 1.1),
        "ttfb_ms": int(fetch_result.page_load_ms * 0.35),
        "error_code": error_code,
        "error_message": error_message,
        "fallback_reason": fallback_reason,
        "raw": {
            "page_size_kb": round(page_size_kb, 1),
            "page_load_ms": fetch_result.page_load_ms,
        },
    }


def _is_transient_pagespeed_error(error: requests.RequestException) -> bool:
    if isinstance(error, requests.Timeout):
        return True
    if isinstance(error, requests.HTTPError):
        status_code = getattr(getattr(error, "response", None), "status_code", None)
        if status_code == 429:
            return True
        return bool(status_code and 500 <= status_code < 600)
    return False


def _error_diagnostics(error: requests.RequestException) -> tuple[str, str]:
    if isinstance(error, requests.Timeout):
        return "TIMEOUT", "Request to PageSpeed API timed out"
    if isinstance(error, requests.HTTPError):
        status_code = getattr(getattr(error, "response", None), "status_code", None)
        if status_code:
            return f"HTTP_{status_code}", f"PageSpeed API returned HTTP {status_code}"
        return "HTTP_ERROR", "PageSpeed API returned an HTTP error"
    if isinstance(error, requests.ConnectionError):
        return "CONNECTION_ERROR", "Connection to PageSpeed API failed"
    return (
        error.__class__.__name__.upper(),
        str(error) or "Unknown PageSpeed error",
    )


def _log_pagespeed_fallback(
    url: str,
    error: requests.RequestException,
    timeout: float,
    min_interval_seconds: float,
    retries: int,
    retry_count: int,
) -> None:
    logger = current_app.logger if has_app_context() else logging.getLogger(__name__)
    logger.warning(
        (
            "PageSpeed fallback activated for url=%s due_to=%s "
            "(timeout=%.2fs, min_interval=%.2fs, "
            "configured_retries=%s, attempted_retries=%s)"
        ),
        url,
        error.__class__.__name__,
        timeout,
        min_interval_seconds,
        retries,
        retry_count,
    )
