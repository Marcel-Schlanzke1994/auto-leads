from __future__ import annotations

from urllib.parse import urlparse

from auto_leads.models import Lead


def extract_domain(url: str | None) -> str | None:
    if not url:
        return None
    try:
        host = urlparse(url).hostname
    except ValueError:
        return None
    return host.lower() if host else None


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

    query = Lead.query.filter(Lead.company_name.ilike(company_name))
    if query.first():
        return True

    if phone and Lead.query.filter_by(phone=phone).first():
        return True

    if email and Lead.query.filter_by(email=email).first():
        return True

    return False
