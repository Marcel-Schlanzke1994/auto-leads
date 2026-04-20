from __future__ import annotations

from datetime import UTC, datetime
from threading import Thread
from typing import Any

from flask import Flask

from auto_leads.extensions import db
from auto_leads.models import Lead, SearchJob
from auto_leads.services.audit import audit_website
from auto_leads.services.dedupe import is_duplicate_candidate
from auto_leads.services.free_places import FreePlacesError, OpenStreetMapPlacesClient
from auto_leads.services.google_places import GooglePlacesClient, GooglePlacesError
from auto_leads.services.scoring import calculate_lead_score
from auto_leads.utils import normalize_website_url


def start_search_job(
    app: Flask, keyword: str, cities: list[str], radius: int | None = None
) -> SearchJob:
    job = SearchJob(
        keyword=keyword, cities=", ".join(cities), status="queued", message="Wartet"
    )
    db.session.add(job)
    db.session.commit()

    thread = Thread(
        target=_run_search_job, args=(app, job.id, keyword, cities, radius), daemon=True
    )
    thread.start()
    return job


def _run_search_job(
    app: Flask, job_id: int, keyword: str, cities: list[str], radius: int | None
) -> None:
    del radius  # Radius ist für Google Places möglich; OSM ignoriert es aktuell.

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

        queries = [f"{keyword} {city}" for city in cities]
        place_ids: list[tuple[str, str]] = []

        for q in queries:
            try:
                ids = client.text_search(q, max_results=20)
                place_ids.extend((q, pid) for pid in ids)
            except (GooglePlacesError, FreePlacesError):
                job.errors += 1

        job.total = len(place_ids)
        db.session.commit()

        for query, place_id in place_ids:
            try:
                place = client.place_details(place_id)
                city = _extract_city(place.formatted_address or "")
                website = normalize_website_url(place.website)

                if is_duplicate_candidate(
                    place_id=place.place_id,
                    company_name=place.display_name,
                    website=website,
                    phone=place.phone,
                    email=None,
                ):
                    job.skipped_duplicates += 1
                    job.processed += 1
                    db.session.commit()
                    continue

                lead = Lead(
                    company_name=place.display_name,
                    industry=keyword,
                    city=city,
                    address=place.formatted_address,
                    website=website,
                    phone=place.phone,
                    google_place_id=place.place_id,
                    google_rating=place.rating,
                    review_count=place.review_count,
                    source=source_name,
                    source_query=query,
                    categories=place.primary_type,
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
                    except (
                        Exception
                    ) as exc:  # noqa: BLE001 - per lead errors are isolated
                        lead.audit_notes = f"Audit Fehler: {exc}"

                lead.score, reasons = calculate_lead_score(lead)
                lead.score_reasons = "\n".join(reasons)

                db.session.add(lead)
                job.created += 1
            except Exception:
                job.errors += 1
            finally:
                job.processed += 1
                job.message = f"Verarbeitet: {job.processed}/{job.total}"
                db.session.commit()

        job.status = "finished"
        job.finished_at = datetime.now(UTC)
        job.message = "Suche abgeschlossen"
        db.session.commit()


def _create_places_client(app: Flask) -> tuple[Any | None, str, str | None]:
    provider = (app.config.get("PLACES_PROVIDER") or "osm").lower().strip()

    if provider == "google_places":
        api_key = app.config.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return None, "google_places", "GOOGLE_MAPS_API_KEY fehlt"
        return (
            GooglePlacesClient(api_key, timeout=app.config["REQUEST_TIMEOUT"]),
            provider,
            None,
        )

    return (
        OpenStreetMapPlacesClient(timeout=app.config["REQUEST_TIMEOUT"]),
        "osm_nominatim",
        None,
    )


def _extract_city(address: str) -> str | None:
    if not address:
        return None
    parts = [p.strip() for p in address.split(",") if p.strip()]
    return parts[-2] if len(parts) > 1 else parts[-1]
