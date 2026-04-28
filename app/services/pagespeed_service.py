from __future__ import annotations

from app.services.website_fetcher import FetchResult


def extract_page_load_ms(fetch_result: FetchResult) -> int:
    return fetch_result.page_load_ms
