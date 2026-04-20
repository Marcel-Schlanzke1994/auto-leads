from __future__ import annotations

from datetime import UTC, datetime
from threading import Thread
from typing import Any

from flask import Flask

from auto_leads.extensions import db
from auto_leads.models import Lead, SearchJob
from auto_leads.services.audit import audit_website
from auto_leads.services.dedupe import is_duplicate_candidate
from auto_leads.services.google_places import (
    GooglePlacesClient,
    GooglePlacesError,
    PlaceSummary,
)
from auto_leads.services.scoring import calculate_lead_score
from auto_leads.utils import normalize_website_url

SAFETY_MAX_RAW_RESULTS = 3000

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


def start_search_job(
    app: Flask,
    keyword: str,
    cities: list[str],
    radius: int | None = None,
    target_count: int = 1000,
) -> SearchJob:
    del radius
    job = SearchJob(
        keyword=keyword,
        cities=", ".join(cities),
        status="queued",
        message="Wartet",
        target_count=max(1, min(target_count, 1000)),
    )
    db.session.add(job)
    db.session.commit()

    thread = Thread(
        target=_run_search_job,
        args=(app, job.id, keyword, cities),
        daemon=True,
    )
    thread.start()
    return job


def _run_search_job(app: Flask, job_id: int, keyword: str, cities: list[str]) -> None:
    with app.app_context():
        job = db.session.get(SearchJob, job_id)
        if not job:
            return

        client, source_name, provider_error = _create_places_client(app)
        if not client:
            job.status = "failed"
            job.message = provider_error or "Places Provider nicht verfügbar"
            job.finished_at = datetime.now(UTC)
            db.session.commit()
            return

        job.status = "running"
        job.message = f"{source_name} Suche läuft"
        db.session.commit()

        for city in cities:
            if job.total_created >= job.target_count:
                break

            query = f"{keyword} in {city}"
            job.current_city = city
            job.current_query = query
            job.message = f"Suche laufend: {query}"
            db.session.commit()

            remaining = max(0, job.target_count - job.total_created)
            raw_limit = min(max(remaining * 4, 80), SAFETY_MAX_RAW_RESULTS)

            try:
                batch = client.text_search_paginated(
                    query, max_results=raw_limit, safety_page_limit=60
                )
            except GooglePlacesError as exc:
                job.errors += 1
                job.message = f"Text Search Fehler: {exc}"
                db.session.commit()
                continue

            job.total_found_raw += batch.total_found_raw
            db.session.commit()

            for place_id in batch.place_ids:
                if job.total_created >= job.target_count:
                    break

                try:
                    place = client.place_details(place_id)
                    if not _is_relevant_business(place):
                        job.filtered_out += 1
                        continue

                    city_name = _extract_city(
                        place.address_components, place.formatted_address
                    )
                    website = normalize_website_url(place.website)
                    categories = (
                        ", ".join(place.all_types)
                        if place.all_types
                        else place.primary_type
                    )

                    if is_duplicate_candidate(
                        place_id=place.place_id,
                        company_name=place.display_name,
                        website=website,
                        phone=place.phone,
                        email=None,
                    ):
                        job.duplicates_skipped += 1
                        continue

                    lead = Lead(
                        company_name=place.display_name,
                        industry=keyword,
                        city=city_name,
                        address=place.formatted_address,
                        website=website,
                        phone=place.phone,
                        google_place_id=place.place_id,
                        google_rating=place.rating,
                        review_count=place.review_count,
                        source=source_name,
                        source_query=query,
                        categories=categories,
                        status="new",
                    )

                    if lead.website:
                        try:
                            audit = audit_website(
                                lead.website, app.config["REQUEST_TIMEOUT"]
                            )
                            lead.site_title = audit.site_title
                            lead.meta_description = audit.meta_description
                            lead.has_h1 = audit.has_h1
                            lead.has_cta = audit.has_cta
                            lead.mobile_signals = audit.mobile_signals
                            lead.has_contact_info = audit.has_contact_info
                            lead.page_load_ms = audit.page_load_ms
                            lead.impressum_found = audit.impressum_found
                            lead.audit_notes = audit.audit_notes
                            lead.parser_notes = audit.parser_notes
                            lead.checked_pages = audit.checked_pages
                            if not lead.email:
                                lead.email = audit.email
                            if not lead.phone:
                                lead.phone = audit.phone
                            lead.owner_name = audit.owner_name
                            lead.legal_form = audit.legal_form
                        except Exception as exc:  # noqa: BLE001
                            lead.audit_notes = f"Audit Fehler: {exc}"

                    lead.score, reasons = calculate_lead_score(lead)
                    lead.score_reasons = "\n".join(reasons)

                    db.session.add(lead)
                    db.session.commit()
                    job.total_created += 1
                except Exception:
                    job.errors += 1
                finally:
                    job.total_processed += 1
                    job.message = (
                        f"{job.total_created}/{job.target_count} neue Leads · "
                        f"{job.total_processed} verarbeitet"
                    )
                    db.session.commit()

        if job.total_created >= job.target_count:
            job.message = f"Ziel erreicht: {job.total_created} neue Leads"
        elif job.status != "failed":
            job.message = (
                f"Suche abgeschlossen ({job.total_created} neue Leads, "
                f"keine weiteren relevanten Treffer)"
            )

        if job.status != "failed":
            job.status = "finished"
        job.finished_at = datetime.now(UTC)
        db.session.commit()


def _create_places_client(app: Flask) -> tuple[Any | None, str, str | None]:
    provider = (app.config.get("PLACES_PROVIDER") or "google_places").lower().strip()

    if provider != "google_places":
        return None, provider, "Nur PLACES_PROVIDER=google_places wird unterstützt"

    api_key = (app.config.get("GOOGLE_MAPS_API_KEY") or "").strip()
    if not api_key:
        return None, "google_places", "GOOGLE_MAPS_API_KEY fehlt"
    return (
        GooglePlacesClient(api_key, timeout=app.config["REQUEST_TIMEOUT"]),
        provider,
        None,
    )


def _extract_city(
    address_components: list[dict] | None, formatted_address: str | None
) -> str | None:
    components = address_components or []
    city_priority = [
        "locality",
        "postal_town",
        "administrative_area_level_3",
        "administrative_area_level_2",
    ]

    for wanted in city_priority:
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
        cleaned = " ".join(part.split())
        if not cleaned:
            continue
        tokens = cleaned.split()
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


def _is_relevant_business(place: PlaceSummary) -> bool:
    types = {t.lower() for t in place.all_types or []}
    primary_type = (place.primary_type or "").lower()
    if primary_type:
        types.add(primary_type)

    if not types:
        return bool(place.website or place.phone)

    if types & IRRELEVANT_TYPES and not (types & BUSINESS_HINT_TYPES):
        return False

    has_business_context = bool(types & BUSINESS_HINT_TYPES)
    has_minimum_data = bool(
        place.display_name and (place.website or place.phone or place.review_count)
    )
    return has_business_context or has_minimum_data
