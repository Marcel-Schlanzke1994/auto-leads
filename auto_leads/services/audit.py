from __future__ import annotations

import re
import time
from dataclasses import dataclass
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from auto_leads.utils import is_private_hostname

EMAIL_RE = re.compile(r"[\w.\-+%]+@[\w\-]+\.[\w\-.]+")
PHONE_RE = re.compile(r"\+?\d[\d\s/().-]{6,}\d")
LEGAL_FORM_RE = re.compile(r"\b(GmbH|UG|e\.K\.|GbR|OHG|AG|KG|PartG)\b", re.IGNORECASE)
OWNER_RE = re.compile(
    r"(?:Inhaber|Gesch[aä]ftsf[uü]hrer|Vertretungsberechtigt(?:e Person)?)"
    r"\s*:?\s*([^\n|<]{3,120})",
    re.IGNORECASE,
)


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
    parsed = urlparse(url)
    if not parsed.hostname:
        raise ValueError("Ungültige URL")
    if is_private_hostname(parsed.hostname):
        raise ValueError("Private/local targets are blocked")

    session = requests.Session()
    headers = {"User-Agent": "auto-leads/2.0"}

    started = time.perf_counter()
    resp = session.get(url, timeout=timeout, headers=headers, allow_redirects=True)
    resp.raise_for_status()
    load_ms = int((time.perf_counter() - started) * 1000)

    soup = BeautifulSoup(resp.text or "", "html.parser")
    title = soup.title.string.strip() if soup.title and soup.title.string else None
    meta = soup.find("meta", attrs={"name": "description"})
    meta_description = (meta.get("content") or "").strip() or None if meta else None
    page_text = soup.get_text(" ", strip=True).lower()
    has_h1 = bool(soup.find("h1"))
    has_cta = any(
        k in page_text for k in ["kontakt", "anfrage", "termin", "angebot", "call"]
    )
    mobile = bool(
        soup.find("meta", attrs={"name": "viewport"}) or "@media" in (resp.text or "")
    )

    candidate_pages = _collect_candidate_links(soup, resp.url)
    checked = []
    collected_text = [resp.text or ""]
    impressum_found = False

    for page in candidate_pages[:8]:
        checked.append(page)
        try:
            page_resp = session.get(page, timeout=timeout, headers=headers)
            if page_resp.ok:
                body = page_resp.text or ""
                collected_text.append(body)
                if re.search(r"\bimpressum\b|\blegal notice\b", body, re.IGNORECASE):
                    impressum_found = True
        except requests.RequestException:
            continue

    combined = "\n".join(collected_text)
    email = _first_match(EMAIL_RE, combined)
    phone = _first_match(PHONE_RE, combined)
    owner = _extract_owner(combined)
    legal_form = _first_match(LEGAL_FORM_RE, combined)

    notes = [f"Homepage status={resp.status_code}", f"Final URL={resp.url}"]
    parser_notes = [
        "Impressum gefunden" if impressum_found else "Impressum nicht gefunden",
        "E-Mail gefunden" if email else "Keine E-Mail",
        "Telefon gefunden" if phone else "Kein Telefon",
    ]

    return AuditResult(
        site_title=title,
        meta_description=meta_description,
        has_h1=has_h1,
        has_cta=has_cta,
        mobile_signals=mobile,
        has_contact_info=bool(email or phone),
        page_load_ms=load_ms,
        impressum_found=impressum_found,
        email=email,
        phone=phone,
        owner_name=owner,
        legal_form=legal_form,
        parser_notes="\n".join(parser_notes),
        checked_pages="\n".join(checked),
        audit_notes="\n".join(notes),
    )


def _collect_candidate_links(soup: BeautifulSoup, base_url: str) -> list[str]:
    labels = ["impressum", "kontakt", "contact", "über", "about", "legal", "recht"]
    candidates: list[str] = []
    base_host = urlparse(base_url).hostname

    for a in soup.find_all("a", href=True):
        text = (a.get_text(" ", strip=True) or "").lower()
        href = a.get("href", "")
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


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(0).strip() if match else None


def _extract_owner(text: str) -> str | None:
    match = OWNER_RE.search(text)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip(" :;,-")[:120]
