from __future__ import annotations

import re
from urllib.parse import urlparse

from app.models import Lead

LEGAL_FORM_PATTERN = re.compile(
    r"\b(?:gmbh|ug|ag|e\.?\s?k\.?|gbr|kg|ohg|mbh)\b", re.IGNORECASE
)
NON_WORD_PATTERN = re.compile(r"[^\w\s]", re.UNICODE)
SPACE_PATTERN = re.compile(r"\s+")


def normalize_domain(url: str | None) -> str | None:
    if not url:
        return None

    raw = url.strip()
    if not raw:
        return None

    candidate = raw if "://" in raw else f"https://{raw}"
    try:
        host = urlparse(candidate).hostname
    except ValueError:
        return None

    if not host:
        return None

    normalized = host.strip().rstrip(".").lower()
    if normalized.startswith("www."):
        normalized = normalized[4:]

    try:
        normalized = normalized.encode("idna").decode("ascii")
    except UnicodeError:
        return None

    return normalized or None


def normalize_company_name(company_name: str | None) -> str | None:
    if not company_name:
        return None

    cleaned = NON_WORD_PATTERN.sub(" ", company_name.lower()).strip()
    cleaned = LEGAL_FORM_PATTERN.sub(" ", cleaned)
    cleaned = SPACE_PATTERN.sub(" ", cleaned).strip()
    return cleaned or None


def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None

    candidate = phone.strip()
    if not candidate:
        return None

    has_plus = candidate.startswith("+")
    digits = "".join(ch for ch in candidate if ch.isdigit())
    if not digits:
        return None

    if digits.startswith("00"):
        digits = digits[2:]
        has_plus = True

    if has_plus:
        return f"+{digits}"

    return digits


def normalize_email(email: str | None) -> str | None:
    if not email:
        return None

    normalized = email.strip().lower()
    return normalized or None


def normalize_city(city: str | None) -> str | None:
    if not city:
        return None
    normalized = SPACE_PATTERN.sub(" ", city.strip().lower())
    return normalized or None


def is_duplicate(
    *,
    place_id: str | None,
    company_name: str | None,
    city: str | None,
    website: str | None,
    phone: str | None,
    email: str | None,
) -> bool:
    normalized_domain = normalize_domain(website)
    normalized_name = normalize_company_name(company_name)
    normalized_phone = normalize_phone(phone)
    normalized_email = normalize_email(email)
    normalized_city = normalize_city(city)

    if place_id and Lead.query.filter_by(google_place_id=place_id).first():
        return True

    if normalized_domain and Lead.query.filter_by(domain=normalized_domain).first():
        return True

    if (
        normalized_phone
        and Lead.query.filter_by(phone_normalized=normalized_phone).first()
    ):
        return True

    if (
        normalized_email
        and Lead.query.filter_by(email_normalized=normalized_email).first()
    ):
        return True

    if normalized_name and normalized_city:
        if Lead.query.filter_by(
            normalized_company_name=normalized_name,
            city_normalized=normalized_city,
        ).first():
            return True

    # Name-only matches are intentionally treated as a weak signal and
    # therefore are not enough to classify a lead as a hard duplicate.
    if (
        normalized_name
        and Lead.query.filter_by(normalized_company_name=normalized_name).first()
    ):
        return False

    return False
