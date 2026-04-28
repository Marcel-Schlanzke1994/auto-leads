from __future__ import annotations

import os

import requests

from app.services.website_fetcher import FetchResult


PSI_API_URL = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed"
PSI_API_KEY = os.getenv("PAGESPEED_API_KEY", "").strip()


def extract_page_load_ms(fetch_result: FetchResult) -> int:
    return fetch_result.page_load_ms


def analyze_pagespeed(url: str, fetch_result: FetchResult, timeout: float) -> dict:
    if PSI_API_KEY:
        try:
            response = requests.get(
                PSI_API_URL,
                timeout=timeout,
                params={"url": url, "strategy": "mobile", "key": PSI_API_KEY},
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
            }
        except requests.RequestException:
            pass

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
        "raw": {
            "page_size_kb": round(page_size_kb, 1),
            "page_load_ms": fetch_result.page_load_ms,
        },
    }


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
