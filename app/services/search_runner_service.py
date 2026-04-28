from __future__ import annotations

import json

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
from app.services.lead_score_service import (
    calculate_lead_score,
    calculate_lead_score_details,
)
from app.services.website_audit_service import audit_website, persist_audit_result
from app.extensions import db
from app.utils import normalize_website_url

DEFAULT_SAFETY_MAX_RAW_RESULTS = 3000
DEFAULT_MAX_TARGET_COUNT = 1000
DEFAULT_TEXT_SEARCH_PAGE_LIMIT = 60


def start_search_job(
    app: Flask,
    keyword: str,
    cities: list[str],
    radius: int | None = None,
    target_count: int = 1000,
) -> SearchJob:
    del radius
    max_target_count = int(
        app.config.get("SEARCH_MAX_TARGET_COUNT", DEFAULT_MAX_TARGET_COUNT)
    )
    bounded_target = max(1, min(target_count, max_target_count))
    job = SearchJob(
        keyword=keyword,
        cities=", ".join(cities),
        status="queued",
        message="Wartet",
        target_count=bounded_target,
        log_json=[],
    )
    db.session.add(job)
    db.session.commit()
    _append_job_event(
        job,
        phase="queued",
        message="Job erstellt und in Warteschlange",
        reason="queued",
    )
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
            _mark_job_failed(job, provider_error or "Places Provider nicht verfügbar")
            return

        job.status = "running"
        job.started_at = job.started_at or datetime.now(UTC)
        job.message = f"{source_name} Suche läuft"
        _append_job_event(job, phase="start", message=job.message)

        max_raw_results = int(
            app.config.get("SEARCH_MAX_RAW_RESULTS", DEFAULT_SAFETY_MAX_RAW_RESULTS)
        )
        text_page_limit = int(
            app.config.get("SEARCH_TEXT_PAGE_LIMIT", DEFAULT_TEXT_SEARCH_PAGE_LIMIT)
        )
        for city in cities:
            if job.total_created >= job.target_count:
                break
            query = f"{keyword} in {city}"
            job.current_city = city
            job.current_query = query
            job.message = f"Suche laufend: {query}"
            _append_job_event(job, phase="city_start", message=job.message)

            remaining = max(0, job.target_count - job.total_created)
            raw_limit = min(max(remaining * 4, 80), max_raw_results)
            try:
                batch = client.text_search_paginated(
                    query,
                    max_results=raw_limit,
                    safety_page_limit=text_page_limit,
                )
            except GooglePlacesError as exc:
                job.errors += 1
                job.message = f"Text Search Fehler: {exc}"
                _append_job_event(
                    job,
                    phase="text_search_error",
                    message=job.message,
                    error=str(exc),
                )
                continue

            job.total_found_raw += batch.total_found_raw
            _append_job_event(
                job,
                phase="text_search_done",
                message=f"{batch.total_found_raw} Roh-Treffer für {query}",
            )

            for place_id in batch.place_ids:
                if job.total_created >= job.target_count:
                    break
                try:
                    place = client.place_details(place_id)
                    if not _is_relevant_business(place):
                        job.filtered_out += 1
                        _append_job_event(
                            job,
                            phase="filtered_out",
                            message=(
                                "Irrelevanter Treffer gefiltert: "
                                f"{place.display_name}"
                            ),
                        )
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
                        _append_job_event(
                            job,
                            phase="duplicate",
                            message=f"Dublette übersprungen: {lead.company_name}",
                        )
                        continue
                    _enrich_lead_with_audit(lead, app)
                    lead.score, _ = calculate_lead_score(lead)
                    lead.score_reasons = json.dumps(
                        calculate_lead_score_details(lead), ensure_ascii=False
                    )
                    db.session.add(lead)
                    db.session.commit()
                    job.total_created += 1
                    _append_job_event(
                        job,
                        phase="lead_created",
                        message=f"Neuer Lead: {lead.company_name}",
                    )
                except Exception as exc:  # noqa: BLE001
                    job.errors += 1
                    _append_job_event(
                        job,
                        phase="lead_error",
                        message=f"Fehler bei Place {place_id}",
                        error=str(exc),
                    )
                finally:
                    job.total_processed += 1
                    job.message = (
                        f"{job.total_created}/{job.target_count} neue Leads · "
                        f"{job.total_processed} verarbeitet"
                    )
                    db.session.commit()

        if job.total_created >= job.target_count:
            reason = "target_reached"
            job.message = f"Ziel erreicht: {job.total_created} neue Leads"
        else:
            reason = "no_more_results"
            job.message = (
                f"Suche abgeschlossen ({job.total_created} neue Leads, "
                "keine weiteren relevanten Treffer)"
            )
        job.status = "finished"
        job.finished_at = datetime.now(UTC)
        _append_job_event(job, phase="finished", message=job.message, reason=reason)


def _mark_job_failed(job: SearchJob, reason: str) -> None:
    job.status = "failed"
    job.message = reason
    job.finished_at = datetime.now(UTC)
    _append_job_event(
        job, phase="failed", message=reason, reason="provider_unavailable", error=reason
    )


def _job_counters(job: SearchJob) -> dict[str, int]:
    return {
        "target": min(job.target_count or 0, DEFAULT_MAX_TARGET_COUNT),
        "raw_found": job.total_found_raw,
        "processed": job.total_processed,
        "new_leads": job.total_created,
        "duplicates": job.duplicates_skipped,
        "filtered_out": job.filtered_out,
        "errors": job.errors,
    }


def _append_job_event(
    job: SearchJob,
    *,
    phase: str,
    message: str,
    error: str | None = None,
    reason: str | None = None,
) -> None:
    events = list(job.log_json or [])
    events.append(
        {
            "timestamp": datetime.now(UTC).isoformat(),
            "status": job.status,
            "city": job.current_city,
            "query": job.current_query,
            "phase": phase,
            "message": message,
            "reason": reason,
            "error": error,
            "counters": _job_counters(job),
        }
    )
    job.log_json = events
    db.session.commit()


def _create_places_client(app: Flask) -> tuple[Any | None, str, str | None]:
    provider = (app.config.get("PLACES_PROVIDER") or "google_places").lower().strip()
    if provider != "google_places":
        return None, provider, "Nur PLACES_PROVIDER=google_places wird unterstützt"
    api_key = (app.config.get("GOOGLE_MAPS_API_KEY") or "").strip()
    if not api_key:
        return None, "google_places", "GOOGLE_MAPS_API_KEY fehlt"
    policy = app.config["EXTERNAL_SERVICE_POLICIES"]["google_places"]
    return (
        GooglePlacesClient(
            api_key,
            timeout=policy.timeout,
            min_interval_seconds=policy.min_interval_seconds,
            retry_max_attempts=app.config.get("GOOGLE_PLACES_RETRY_MAX_ATTEMPTS", 4),
            retry_backoff_base=app.config.get("GOOGLE_PLACES_RETRY_BACKOFF_BASE", 0.5),
            retry_max_delay=app.config.get("GOOGLE_PLACES_RETRY_MAX_DELAY", 8.0),
            retry_jitter=app.config.get("GOOGLE_PLACES_RETRY_JITTER", 0.3),
        ),
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
