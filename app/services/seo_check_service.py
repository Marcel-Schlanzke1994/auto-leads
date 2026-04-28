from __future__ import annotations

from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass(slots=True)
class SeoSignals:
    site_title: str | None
    meta_description: str | None
    has_h1: bool
    has_cta: bool
    mobile_signals: bool


def analyze_seo(html: str) -> SeoSignals:
    soup = BeautifulSoup(html, "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta = soup.find("meta", attrs={"name": "description"})
    meta_description = (meta.get("content") or "").strip() or None if meta else None
    page_text = soup.get_text(" ", strip=True).lower()
    return SeoSignals(
        site_title=title,
        meta_description=meta_description,
        has_h1=bool(soup.find("h1")),
        has_cta=any(
            k in page_text for k in ["kontakt", "anfrage", "termin", "angebot", "call"]
        ),
        mobile_signals=bool(
            soup.find("meta", attrs={"name": "viewport"}) or "@media" in html
        ),
    )
