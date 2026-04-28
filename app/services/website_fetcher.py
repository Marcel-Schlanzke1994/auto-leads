from __future__ import annotations

import time
from dataclasses import dataclass
from urllib.parse import urlparse

import requests

from auto_leads.utils import is_private_hostname


@dataclass(slots=True)
class FetchResult:
    url: str
    body: str
    status_code: int
    page_load_ms: int


def fetch_website(
    url: str, timeout: float, session: requests.Session | None = None
) -> FetchResult:
    parsed = urlparse(url)
    if not parsed.hostname:
        raise ValueError("Ungültige URL")
    if is_private_hostname(parsed.hostname):
        raise ValueError("Private/local targets are blocked")

    http = session or requests.Session()
    started = time.perf_counter()
    response = http.get(
        url,
        timeout=timeout,
        headers={"User-Agent": "auto-leads/2.0"},
        allow_redirects=True,
    )
    response.raise_for_status()
    return FetchResult(
        url=response.url,
        body=response.text or "",
        status_code=response.status_code,
        page_load_ms=int((time.perf_counter() - started) * 1000),
    )
