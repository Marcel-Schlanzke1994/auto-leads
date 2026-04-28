from __future__ import annotations

from datetime import UTC, datetime
from threading import Thread
from typing import Any

from flask import Flask

from app.models import Lead, SearchJob
from app.services.duplicate_service import (
    is_duplicate,
    normalize_city,
    normalize_company_name,
    normalize_domain,
    normalize_email,
    normalize_phone,
)
from app.services.extraction_service import extract_city, is_relevant_business
from app.services.google_places_service import (
    GooglePlacesClient,
    GooglePlacesError,
    PlaceSummary,
)
from app.services.lead_score_service import calculate_lead_score
from app.services.website_audit_service import audit_website, persist_audit_result
from auto_leads.extensions import db
from auto_leads.utils import normalize_website_url

SAFETY_MAX_RAW_RESULTS = 3000


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
    Thread(
        target=_run_search_job, args=(app, job.id, keyword, cities), daemon=True
    ).start()
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
                    lead = _build_lead(place, keyword, query)
                    if is_duplicate(
                        place_id=lead.google_place_id,
                        company_name=lead.company_name,
                        city=lead.city,
                        website=lead.website,
                        phone=lead.phone,
                        email=lead.email,
                    ):
                        job.duplicates_skipped += 1
                        continue
                    _enrich_lead_with_audit(lead, app)
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
                "keine weiteren relevanten Treffer)"
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


def _build_lead(place: PlaceSummary, keyword: str, query: str) -> Lead:
    city = _extract_city(place.address_components, place.formatted_address)
    website = normalize_website_url(place.website)

    return Lead(
        company_name=place.display_name,
        normalized_company_name=normalize_company_name(place.display_name),
        industry=keyword,
        city=city,
        city_normalized=normalize_city(city),
        address=place.formatted_address,
        website=website,
        domain=normalize_domain(website),
        phone=place.phone,
        phone_normalized=normalize_phone(place.phone),
        google_place_id=place.place_id,
        google_rating=place.rating,
        review_count=place.review_count,
        source="google_places",
        source_query=query,
        categories=(
            ", ".join(place.all_types) if place.all_types else place.primary_type
        ),
        status="new",
    )


def _enrich_lead_with_audit(lead: Lead, app: Flask) -> None:
    if not lead.website:
        return
    try:
        audit = audit_website(lead.website, app.config["REQUEST_TIMEOUT"])
    except Exception as exc:  # noqa: BLE001
        lead.audit_notes = f"Audit Fehler: {exc}"
        return

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

    lead.domain = normalize_domain(lead.website)
    lead.normalized_company_name = normalize_company_name(lead.company_name)
    lead.city_normalized = normalize_city(lead.city)
    lead.phone_normalized = normalize_phone(lead.phone)
    lead.email_normalized = normalize_email(lead.email)

    lead.owner_name = audit.owner_name
    lead.legal_form = audit.legal_form
    persist_audit_result(lead, audit)


def _extract_city(
    address_components: list[dict] | None, formatted_address: str | None
) -> str | None:
    return extract_city(address_components, formatted_address)


def _is_relevant_business(place: PlaceSummary) -> bool:
    return is_relevant_business(place)
