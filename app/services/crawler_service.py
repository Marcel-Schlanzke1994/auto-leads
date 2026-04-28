from __future__ import annotations

import re
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def collect_candidate_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    labels = ["impressum", "kontakt", "contact", "über", "about", "legal", "recht"]
    candidates: list[str] = []
    base_host = urlparse(base_url).hostname
    for anchor in soup.find_all("a", href=True):
        text = (anchor.get_text(" ", strip=True) or "").lower()
        href = anchor.get("href", "")
        if not any(label in text or label in href.lower() for label in labels):
            continue
        full = urljoin(base_url, href)
        host = urlparse(full).hostname
        if (
            host
            and base_host
            and host.lower() == base_host.lower()
            and full not in candidates
        ):
            candidates.append(full)

    for path in [
        "/impressum",
        "/kontakt",
        "/contact",
        "/about",
        "/ueber-uns",
        "/ueber_uns",
    ]:
        full = urljoin(base_url, path)
        if full not in candidates:
            candidates.append(full)
    return candidates


def crawl_related_pages(
    base_url: str, soup: BeautifulSoup, timeout: float, session: requests.Session
) -> tuple[list[str], str, bool]:
    checked: list[str] = []
    bodies: list[str] = []
    impressum_found = False
    for page in collect_candidate_links(soup, base_url)[:8]:
        checked.append(page)
        try:
            page_resp = session.get(
                page, timeout=timeout, headers={"User-Agent": "auto-leads/2.0"}
            )
            if page_resp.ok:
                body = page_resp.text or ""
                bodies.append(body)
                if re.search(r"\bimpressum\b|\blegal notice\b", body, re.IGNORECASE):
                    impressum_found = True
        except requests.RequestException:
            continue
    return checked, "\n".join(bodies), impressum_found
