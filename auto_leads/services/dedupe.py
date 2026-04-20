from __future__ import annotations

from urllib.parse import urlparse

from sqlalchemy import func

from auto_leads.models import Lead


def extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        host = urlparse(url).hostname
    except ValueError:
        return None
    return host.lower() if host else None


def _normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = "".join(ch for ch in phone if ch.isdigit() or ch == "+")
    return digits or None


def is_duplicate_candidate(
    *,
    place_id: str | None,
    company_name: str,
    website: str | None,
    phone: str | None,
    email: str | None,
) -> bool:
    domain = extract_domain(website)

    if place_id and Lead.query.filter_by(google_place_id=place_id).first():
        return True

    if domain:
        for lead in Lead.query.filter(Lead.website.isnot(None)).all():
            if extract_domain(lead.website) == domain:
                return True

    normalized_name = company_name.strip().lower()
    if (
        normalized_name
        and Lead.query.filter(func.lower(Lead.company_name) == normalized_name).first()
    ):
        return True

    normalized_phone = _normalize_phone(phone)
    if normalized_phone:
        for lead in Lead.query.filter(Lead.phone.isnot(None)).all():
            if _normalize_phone(lead.phone) == normalized_phone:
                return True

    normalized_email = (email or "").strip().lower()
    if (
        normalized_email
        and Lead.query.filter(func.lower(Lead.email) == normalized_email).first()
    ):
        return True

    return False
