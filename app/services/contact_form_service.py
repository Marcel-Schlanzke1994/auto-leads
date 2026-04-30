from __future__ import annotations

import json
import re
from dataclasses import dataclass
from urllib.parse import urlparse

from app.models import AuditResult, Lead
from app.services.outreach_draft_service import FIXED_SIGNATURE

CONTACT_HINT_PATTERN = re.compile(
    r"(kontakt|contact|kontaktformular|contact-form|reach-us|get-in-touch|support)",
    re.IGNORECASE,
)
URL_PATTERN = re.compile(r"https?://[^\s<>'\"]+")


@dataclass(slots=True)
class ContactFormDraft:
    subject: str
    body: str
    target_urls: list[str]


def detect_contact_form_urls(
    lead: Lead,
    latest_audit: AuditResult | None = None,
    limit: int = 5,
) -> list[str]:
    """Detect likely contact form URLs from stored crawl/audit artifacts only."""
    candidates: list[str] = []

    candidates.extend(_urls_from_checked_pages(lead.checked_pages))
    candidates.extend(_urls_from_text(lead.audit_notes))

    if latest_audit:
        candidates.extend(_urls_from_text(latest_audit.checked_url))
        candidates.extend(_urls_from_text(latest_audit.redirected_url))
        candidates.extend(_urls_from_meta(latest_audit.meta_json))
        candidates.extend(_urls_from_raw_audit(latest_audit.raw_audit_json))

    if lead.website:
        normalized_base = _normalize_url(lead.website)
        if normalized_base:
            candidates.extend(
                [
                    f"{normalized_base.rstrip('/')}/kontakt",
                    f"{normalized_base.rstrip('/')}/contact",
                ]
            )

    return _rank_and_deduplicate(candidates, limit=limit)


def merge_contact_form_urls(
    existing: list[str] | None, new_urls: list[str]
) -> list[str]:
    merged = list(existing or [])
    for url in new_urls:
        if url not in merged:
            merged.append(url)
    return merged


def build_contact_form_draft(lead: Lead, target_urls: list[str]) -> ContactFormDraft:
    company = lead.company_name or "Ihr Team"
    subject = f"Kontaktformular-Draft für {company}"
    if target_urls:
        targets = "\n".join(f"- {url}" for url in target_urls)
    else:
        targets = "- Keine Kontakt-URL erkannt (manuelle Prüfung empfohlen)."

    body = (
        f"Guten Tag {company},\n\n"
        "wir haben Ihre Website analysiert und erste "
        "Optimierungspotenziale identifiziert. Wenn Sie möchten, senden wir "
        "Ihnen eine kurze Prioritätenliste als unverbindlichen Entwurf.\n\n"
        "Vorgesehene Kontaktseiten (nur Draft, kein Versand):\n"
        f"{targets}\n\n"
        f"{FIXED_SIGNATURE}"
    )
    return ContactFormDraft(subject=subject, body=body, target_urls=target_urls)


def _urls_from_checked_pages(checked_pages: str | None) -> list[str]:
    urls: list[str] = []
    for line in (checked_pages or "").splitlines():
        normalized = _normalize_url(line.strip())
        if normalized and CONTACT_HINT_PATTERN.search(normalized):
            urls.append(normalized)
    return urls


def _urls_from_text(value: str | None) -> list[str]:
    if not value:
        return []
    urls = []
    for raw in URL_PATTERN.findall(value):
        normalized = _normalize_url(raw)
        if normalized and CONTACT_HINT_PATTERN.search(normalized):
            urls.append(normalized)
    return urls


def _urls_from_meta(meta_json: dict | None) -> list[str]:
    if not isinstance(meta_json, dict):
        return []
    urls: list[str] = []
    for key, value in meta_json.items():
        if "contact" not in str(key).lower() and "kontakt" not in str(key).lower():
            continue
        urls.extend(_urls_from_text(str(value)))
    return urls


def _urls_from_raw_audit(raw_audit_json: dict | None) -> list[str]:
    if not isinstance(raw_audit_json, dict):
        return []

    text = json.dumps(raw_audit_json, ensure_ascii=False)
    return _urls_from_text(text)


def _rank_and_deduplicate(urls: list[str], limit: int) -> list[str]:
    seen: set[str] = set()
    ranked: list[tuple[int, str]] = []
    for url in urls:
        normalized = _normalize_url(url)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        score = 0
        path = urlparse(normalized).path.lower()
        if any(token in path for token in ["kontaktformular", "contact-form", "form"]):
            score += 3
        if any(token in path for token in ["kontakt", "contact"]):
            score += 2
        if path.count("/") <= 1:
            score += 1
        ranked.append((score, normalized))

    ranked.sort(key=lambda item: (-item[0], item[1]))
    return [url for _, url in ranked[:limit]]


def _normalize_url(value: str | None) -> str | None:
    if not value:
        return None
    stripped = value.strip().rstrip(",.;")
    parsed = urlparse(stripped)
    if not parsed.scheme:
        return None
    if parsed.scheme not in {"http", "https"}:
        return None
    return parsed._replace(fragment="").geturl()
