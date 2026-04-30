from __future__ import annotations

import os
from urllib.parse import urljoin

from app.services.browser.contact_form_detector import detect_forms_from_html
from app.services.browser.models import BrowserAnalysisResult
from app.services.sandbox import (
    MAX_ANALYSIS_SECONDS,
    MAX_PAGES_PER_LEAD,
    validate_external_url,
)

CONTACT_HINTS = [
    "kontakt",
    "contact",
    "anfrage",
    "termin",
    "impressum",
    "beratung",
    "angebot",
]


def analyze_contact_forms(url: str, html: str | None = None) -> BrowserAnalysisResult:
    try:
        root = validate_external_url(url).normalized_url
    except Exception as exc:
        return BrowserAnalysisResult(url=url, status="failed", errors=[str(exc)])

    enabled = os.getenv("PLAYWRIGHT_ANALYSIS_ENABLED", "false").lower() in {
        "1",
        "true",
        "yes",
        "on",
    }
    if not enabled:
        return BrowserAnalysisResult(
            url=root, status="skipped", metadata={"reason": "disabled"}
        )

    try:
        from playwright.sync_api import sync_playwright
    except Exception as exc:
        return BrowserAnalysisResult(
            url=root, status="unavailable", errors=[f"playwright unavailable: {exc}"]
        )

    browser_name = os.getenv("PLAYWRIGHT_BROWSER", "chromium")
    page_limit = min(
        int(os.getenv("PLAYWRIGHT_MAX_PAGES_PER_LEAD", MAX_PAGES_PER_LEAD)),
        MAX_PAGES_PER_LEAD,
    )
    with sync_playwright() as p:
        browser_type = getattr(p, browser_name)
        browser = browser_type.launch()
        page = browser.new_page()
        page.goto(
            root, wait_until="domcontentloaded", timeout=MAX_ANALYSIS_SECONDS * 1000
        )
        home_html = html or page.content()
        candidates = _contact_candidates(root, home_html)[:page_limit]
        best_url = root
        best_forms = detect_forms_from_html(home_html)
        best_score = sum(f.confidence for f in best_forms)
        for candidate in candidates:
            page.goto(
                candidate,
                wait_until="domcontentloaded",
                timeout=MAX_ANALYSIS_SECONDS * 1000,
            )
            forms = detect_forms_from_html(page.content())
            score = sum(f.confidence for f in forms)
            if score > best_score:
                best_url, best_forms, best_score = candidate, forms, score
        browser.close()

    flattened = [f for form in best_forms for f in form.fields]
    return BrowserAnalysisResult(
        url=root,
        status="success",
        contact_page_url=best_url,
        forms_found=best_forms,
        fields=flattened,
        recommendations=[
            "Kein automatisches Absenden. Nur manuelle Prüfung und Draft-Nutzung."
        ],
        metadata={"candidates_checked": len(candidates)},
    )


def _contact_candidates(base_url: str, html: str) -> list[str]:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html or "", "html.parser")
    candidates: list[tuple[int, str]] = []
    for link in soup.find_all("a"):
        href = (link.get("href") or "").strip()
        text = link.get_text(" ", strip=True).lower()
        if not href:
            continue
        abs_url = urljoin(base_url, href)
        try:
            normalized = validate_external_url(abs_url).normalized_url
        except Exception:
            continue
        score = sum(1 for h in CONTACT_HINTS if h in text or h in normalized.lower())
        if score > 0:
            candidates.append((score, normalized))
    candidates.sort(key=lambda x: (-x[0], x[1]))
    seen = set()
    ordered = []
    for _, candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        ordered.append(candidate)
    return ordered
