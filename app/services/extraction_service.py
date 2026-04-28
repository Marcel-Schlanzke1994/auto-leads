from __future__ import annotations

import re
from dataclasses import dataclass

from app.services.google_places_service import PlaceSummary

EMAIL_RE = re.compile(r"[\w.\-+%]+@[\w\-]+\.[\w\-.]+")
PHONE_RE = re.compile(r"\+?\d[\d\s/().-]{6,}\d")
LEGAL_FORM_RE = re.compile(
    r"\b(GmbH|UG|e\.K\.|GbR|OHG|AG|KG|PartG|Gbr|UG \(haftungsbeschränkt\))\b",
    re.IGNORECASE,
)
OWNER_RE = re.compile(
    r"(?:Inhaber|Gesch[aä]ftsf[uü]hrer|Vertretungsberechtigt(?:e Person)?)"
    r"\s*:?\s*([^\n|<]{3,120})",
    re.IGNORECASE,
)
ADDRESS_RE = re.compile(
    r"\b([A-ZÄÖÜ][\wÄÖÜäöüß\-. ]+\s\d+[a-zA-Z]?,\s?\d{4,5}\s[A-ZÄÖÜ][\wÄÖÜäöüß\-. ]+)\b"
)
OPENING_HOURS_RE = re.compile(
    r"(Mo(?:ntag)?\s*[\-–:]\s*Fr(?:eitag)?[^\n]{5,80}|opening\s*hours[^\n]{2,80})",
    re.IGNORECASE,
)

IRRELEVANT_TYPES = {
    "tourist_attraction",
    "lodging",
    "campground",
    "rv_park",
    "amusement_park",
    "museum",
    "park",
    "zoo",
    "stadium",
    "landmark",
    "church",
    "cemetery",
    "premise",
    "subpremise",
    "route",
    "street_address",
    "intersection",
    "transit_station",
    "airport",
    "school",
    "university",
    "hospital",
    "locality",
    "political",
    "natural_feature",
}
BUSINESS_HINT_TYPES = {
    "roofing_contractor",
    "plumber",
    "electrician",
    "locksmith",
    "general_contractor",
    "real_estate_agency",
    "store",
    "car_repair",
    "beauty_salon",
    "lawyer",
    "accounting",
    "moving_company",
    "insurance_agency",
    "dentist",
    "veterinary_care",
    "restaurant",
    "bakery",
    "gym",
    "car_dealer",
    "travel_agency",
    "florist",
}


@dataclass(slots=True)
class ExtractionProfile:
    email: str | None
    phone: str | None
    owner_name: str | None
    legal_form: str | None
    address: str | None
    opening_hours: str | None
    social_links: list[str]
    whatsapp_links: list[str]
    booking_links: list[str]


def extract_company_profile(text: str) -> ExtractionProfile:
    email = _first_match(EMAIL_RE, text)
    phone = _first_match(PHONE_RE, text)
    owner = _extract_owner(text)
    legal_form = _first_match(LEGAL_FORM_RE, text)
    address = _first_match(ADDRESS_RE, text)
    opening_hours = _first_match(OPENING_HOURS_RE, text)
    socials = _extract_links(
        text,
        ["facebook.com", "instagram.com", "linkedin.com", "tiktok.com", "youtube.com"],
    )
    whatsapp = _extract_links(text, ["wa.me", "whatsapp.com"])
    booking = _extract_links(
        text, ["booking", "book", "termin", "reservierung", "calendly.com"]
    )
    return ExtractionProfile(
        email=email,
        phone=phone,
        owner_name=owner,
        legal_form=legal_form,
        address=address,
        opening_hours=opening_hours,
        social_links=socials,
        whatsapp_links=whatsapp,
        booking_links=booking,
    )


def extract_contact_details(
    text: str,
) -> tuple[str | None, str | None, str | None, str | None]:
    profile = extract_company_profile(text)
    return profile.email, profile.phone, profile.owner_name, profile.legal_form


def extract_city(
    address_components: list[dict] | None, formatted_address: str | None
) -> str | None:
    components = address_components or []
    for wanted in [
        "locality",
        "postal_town",
        "administrative_area_level_3",
        "administrative_area_level_2",
    ]:
        for component in components:
            types = component.get("types") or []
            if wanted in types:
                text = (
                    component.get("longText") or component.get("shortText") or ""
                ).strip()
                if text:
                    return text

    if not formatted_address:
        return None

    parts = [p.strip() for p in formatted_address.split(",") if p.strip()]
    for part in parts:
        tokens = " ".join(part.split()).split()
        if tokens and tokens[0].isdigit() and len(tokens) > 1:
            candidate = " ".join(tokens[1:])
            if any(char.isalpha() for char in candidate):
                return candidate

    for part in reversed(parts):
        cleaned = " ".join(part.split())
        lower = cleaned.lower()
        if lower in {"deutschland", "germany"}:
            continue
        if (
            any(char.isalpha() for char in cleaned)
            and not cleaned.replace(" ", "").isdigit()
        ):
            if cleaned and not cleaned[:1].isdigit() and not lower.startswith("de-"):
                return cleaned
    return None


def is_relevant_business(place: PlaceSummary) -> bool:
    types = {item.lower() for item in place.all_types or []}
    if place.primary_type:
        types.add(place.primary_type.lower())
    if not types:
        return bool(place.website or place.phone)
    if types & IRRELEVANT_TYPES and not (types & BUSINESS_HINT_TYPES):
        return False
    has_business_context = bool(types & BUSINESS_HINT_TYPES)
    has_minimum_data = bool(
        place.display_name and (place.website or place.phone or place.review_count)
    )
    return has_business_context or has_minimum_data


def _first_match(pattern: re.Pattern[str], text: str) -> str | None:
    match = pattern.search(text)
    return match.group(0).strip() if match else None


def _extract_owner(text: str) -> str | None:
    match = OWNER_RE.search(text)
    if not match:
        return None
    return re.sub(r"\s+", " ", match.group(1)).strip(" :;,-")[:120]


def _extract_links(text: str, keywords: list[str]) -> list[str]:
    links: list[str] = []
    for token in text.split():
        if "http" not in token.lower():
            continue
        cleaned = token.strip("()[]<>,.;\"'")
        if (
            any(keyword in cleaned.lower() for keyword in keywords)
            and cleaned not in links
        ):
            links.append(cleaned)
    return links
