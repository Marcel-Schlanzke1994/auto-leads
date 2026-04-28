from __future__ import annotations

import os
import re
import time
from collections import deque
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from flask import current_app, has_app_context


DEFAULT_CRAWL_MAX_PAGES = int(os.getenv("CRAWL_MAX_PAGES", "10"))
DEFAULT_CRAWL_DELAY_SECONDS = float(os.getenv("CRAWL_DELAY_SECONDS", "0.1"))
DEFAULT_USER_AGENT = "auto-leads/3.0 (+website-audit)"


@dataclass(slots=True)
class CrawledPage:
    url: str
    status_code: int
    page_type: str


@dataclass(slots=True)
class CrawlResult:
    checked_pages: list[str]
    combined_text: str
    impressum_found: bool
    redirects: list[str]
    broken_links: list[str]
    important_pages: dict[str, str]
    pages: list[CrawledPage]


def _classify_page(url: str, html: str) -> str:
    path = urlparse(url).path.lower()
    markers = {
        "impressum": ["impressum", "legal", "legal-notice"],
        "kontakt": ["kontakt", "contact"],
        "datenschutz": ["privacy", "datenschutz"],
        "leistungen": ["services", "leistungen", "angebot"],
        "booking": ["booking", "book", "reservierung", "appointment", "termin"],
    }
    for page_type, keys in markers.items():
        if any(key in path for key in keys):
            return page_type
    page_text = html.lower()
    if "öffnungszeiten" in page_text or "opening hours" in page_text:
        return "opening_hours"
    return "generic"


def _extract_internal_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    base_host = urlparse(base_url).hostname or ""
    links: list[str] = []
    for anchor in soup.find_all("a", href=True):
        full = urljoin(base_url, anchor["href"])
        parsed = urlparse(full)
        if (parsed.hostname or "").lower() != base_host.lower():
            continue
        cleaned = parsed._replace(fragment="").geturl()
        if cleaned not in links:
            links.append(cleaned)
    return links


def crawl_related_pages(
    base_url: str,
    soup: BeautifulSoup,
    timeout: float,
    session: requests.Session,
    max_pages: int | None = None,
    delay_seconds: float | None = None,
) -> tuple[list[str], str, bool]:
    result = crawl_domain_pages(
        base_url=base_url,
        seed_soup=soup,
        timeout=timeout,
        session=session,
        max_pages=max_pages,
        delay_seconds=delay_seconds,
    )
    return result.checked_pages, result.combined_text, result.impressum_found


def crawl_domain_pages(
    base_url: str,
    seed_soup: BeautifulSoup,
    timeout: float,
    session: requests.Session,
    max_pages: int | None = None,
    delay_seconds: float | None = None,
) -> CrawlResult:
    max_count = max_pages if max_pages is not None else DEFAULT_CRAWL_MAX_PAGES
    delay = delay_seconds if delay_seconds is not None else DEFAULT_CRAWL_DELAY_SECONDS
    user_agent = DEFAULT_USER_AGENT
    if has_app_context():
        max_count = (
            max_pages
            if max_pages is not None
            else int(current_app.config.get("CRAWL_MAX_PAGES", DEFAULT_CRAWL_MAX_PAGES))
        )
        delay = (
            delay_seconds
            if delay_seconds is not None
            else float(
                current_app.config.get(
                    "CRAWL_DELAY_SECONDS", DEFAULT_CRAWL_DELAY_SECONDS
                )
            )
        )
        user_agent = current_app.config.get("USER_AGENT", DEFAULT_USER_AGENT)
    headers = {"User-Agent": user_agent}

    queue = deque([base_url])
    for link in _extract_internal_links(seed_soup, base_url):
        queue.append(link)

    visited: set[str] = set()
    checked_pages: list[str] = []
    bodies: list[str] = []
    redirects: list[str] = []
    broken_links: list[str] = []
    important_pages: dict[str, str] = {}
    pages: list[CrawledPage] = []
    impressum_found = False

    while queue and len(checked_pages) < max_count:
        target = queue.popleft()
        if target in visited:
            continue
        visited.add(target)
        checked_pages.append(target)
        try:
            page_resp = session.get(
                target,
                timeout=timeout,
                headers=headers,
                allow_redirects=False,
            )
            status_code = page_resp.status_code
            if status_code in {301, 302}:
                redirects.append(f"{target} -> {page_resp.headers.get('Location', '')}")
            if status_code == 404:
                broken_links.append(target)
            if 200 <= status_code < 300:
                body = page_resp.text or ""
                bodies.append(body)
                page_type = _classify_page(target, body)
                pages.append(
                    CrawledPage(
                        url=target, status_code=status_code, page_type=page_type
                    )
                )
                if page_type != "generic" and page_type not in important_pages:
                    important_pages[page_type] = target
                if re.search(r"\bimpressum\b|\blegal notice\b", body, re.IGNORECASE):
                    impressum_found = True
                nested_soup = BeautifulSoup(body, "html.parser")
                for nested in _extract_internal_links(nested_soup, base_url):
                    if nested not in visited:
                        queue.append(nested)
            else:
                pages.append(
                    CrawledPage(
                        url=target, status_code=status_code, page_type="generic"
                    )
                )
        except requests.RequestException:
            broken_links.append(target)
        time.sleep(delay)

    return CrawlResult(
        checked_pages=checked_pages,
        combined_text="\n".join(bodies),
        impressum_found=impressum_found,
        redirects=redirects,
        broken_links=broken_links,
        important_pages=important_pages,
        pages=pages,
    )
