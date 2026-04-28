from __future__ import annotations

from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup

from app.services.crawler_service import crawl_related_pages
from app.services.extraction_service import extract_contact_details
from app.services.pagespeed_service import extract_page_load_ms
from app.services.seo_check_service import analyze_seo
from app.services.website_fetcher import fetch_website


@dataclass(slots=True)
class AuditResult:
    site_title: str | None
    meta_description: str | None
    has_h1: bool
    has_cta: bool
    mobile_signals: bool
    has_contact_info: bool
    page_load_ms: int | None
    impressum_found: bool
    email: str | None
    phone: str | None
    owner_name: str | None
    legal_form: str | None
    parser_notes: str
    checked_pages: str
    audit_notes: str


def audit_website(url: str, timeout: float) -> AuditResult:
    session = requests.Session()
    fetch = fetch_website(url, timeout, session=session)
    seo = analyze_seo(fetch.body)
    soup = BeautifulSoup(fetch.body, "html.parser")
    checked_pages, crawled_text, impressum_found = crawl_related_pages(
        fetch.url, soup, timeout, session
    )
    combined_text = "\n".join([fetch.body, crawled_text])
    email, phone, owner_name, legal_form = extract_contact_details(combined_text)

    parser_notes = [
        "Impressum gefunden" if impressum_found else "Impressum nicht gefunden",
        "E-Mail gefunden" if email else "Keine E-Mail",
        "Telefon gefunden" if phone else "Kein Telefon",
    ]
    audit_notes = [f"Homepage status={fetch.status_code}", f"Final URL={fetch.url}"]

    return AuditResult(
        site_title=seo.site_title,
        meta_description=seo.meta_description,
        has_h1=seo.has_h1,
        has_cta=seo.has_cta,
        mobile_signals=seo.mobile_signals,
        has_contact_info=bool(email or phone),
        page_load_ms=extract_page_load_ms(fetch),
        impressum_found=impressum_found,
        email=email,
        phone=phone,
        owner_name=owner_name,
        legal_form=legal_form,
        parser_notes="\n".join(parser_notes),
        checked_pages="\n".join(checked_pages),
        audit_notes="\n".join(audit_notes),
    )
