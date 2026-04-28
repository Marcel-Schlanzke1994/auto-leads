from __future__ import annotations

import os
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from flask import current_app, has_app_context

from app.services.sandbox import PrivateNetworkBlockedError, validate_external_url
from app.utils import is_private_hostname


DEFAULT_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "8"))
DEFAULT_USER_AGENT = "auto-leads/3.0 (+website-audit)"


@dataclass(slots=True)
class RedirectHop:
    url: str
    status_code: int


@dataclass(slots=True)
class FetchResult:
    requested_url: str
    normalized_url: str
    url: str
    body: str
    status_code: int
    page_load_ms: int
    redirect_history: list[RedirectHop]
    used_https: bool


class WebsiteFetchSecurityError(ValueError):
    """Raised when URL safety checks fail during website fetching."""


def normalize_url(url: str) -> str:
    value = (url or "").strip()
    if not value:
        raise ValueError("Ungültige URL")
    parsed = urlparse(value)
    if not parsed.scheme:
        value = f"https://{value.lstrip('/')}"
    try:
        validated = validate_external_url(value)
    except PrivateNetworkBlockedError as exc:
        raise WebsiteFetchSecurityError("Private/local targets are blocked") from exc
    return validated.normalized_url


def _ensure_public_response_chain(response: requests.Response) -> None:
    redirect_urls = [hop.url for hop in response.history]
    redirect_urls.append(response.url)

    for checked_url in redirect_urls:
        hostname = urlparse(checked_url).hostname
        if not hostname or is_private_hostname(hostname):
            raise WebsiteFetchSecurityError(
                "Redirected to private/local targets are blocked"
            )


def fetch_website(
    url: str,
    timeout: float | None = None,
    session: requests.Session | None = None,
    user_agent: str | None = None,
) -> FetchResult:
    request_timeout = timeout if timeout is not None else DEFAULT_TIMEOUT
    ua = user_agent or DEFAULT_USER_AGENT
    request_delay = 0.0
    if has_app_context():
        policy = current_app.config["EXTERNAL_SERVICE_POLICIES"]["website_fetch"]
        request_timeout = timeout if timeout is not None else policy.timeout
        ua = user_agent or current_app.config.get("USER_AGENT", DEFAULT_USER_AGENT)
        request_delay = policy.min_interval_seconds
    normalized_url = normalize_url(url)

    http = session or requests.Session()
    started = time.perf_counter()
    used_https = normalized_url.lower().startswith("https://")

    try:
        if request_delay > 0:
            time.sleep(request_delay)
        response = http.get(
            normalized_url,
            timeout=request_timeout,
            headers={"User-Agent": ua},
            allow_redirects=True,
        )
    except requests.RequestException:
        if used_https:
            parsed_normalized = urlparse(normalized_url)
            fallback_url = (
                f"http://{parsed_normalized.netloc}" f"{parsed_normalized.path or ''}"
            )
            if parsed_normalized.query:
                fallback_url = f"{fallback_url}?{parsed_normalized.query}"
            if request_delay > 0:
                time.sleep(request_delay)
            response = http.get(
                fallback_url,
                timeout=request_timeout,
                headers={"User-Agent": ua},
                allow_redirects=True,
            )
            used_https = False
            normalized_url = fallback_url
        else:
            raise

    response.raise_for_status()
    _ensure_public_response_chain(response)
    redirect_history = [
        RedirectHop(url=hop.url, status_code=hop.status_code)
        for hop in response.history
    ]
    return FetchResult(
        requested_url=url,
        normalized_url=normalized_url,
        url=response.url,
        body=response.text or "",
        status_code=response.status_code,
        page_load_ms=int((time.perf_counter() - started) * 1000),
        redirect_history=redirect_history,
        used_https=used_https,
    )
