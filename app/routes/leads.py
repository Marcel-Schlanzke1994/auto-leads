from __future__ import annotations

import json
from collections import defaultdict
from datetime import UTC, datetime
from urllib.parse import urlparse

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import or_

from app.models import (
    AuditIssue,
    AuditResult,
    Blacklist,
    ContactAttempt,
    Lead,
    OptOut,
    OutreachDraft,
)
from app.services.contact_form_service import (
    build_contact_form_draft,
    detect_contact_form_urls,
    merge_contact_form_urls,
)
from app.services.lead_score_service import (
    calculate_lead_score,
    calculate_lead_score_details,
)
from app.services.website_audit_service import audit_website, persist_audit_result
from app.extensions import db
from app.forms import OUTREACH_STATUS_LABELS, StatusForm


leads_bp = Blueprint("leads", __name__, url_prefix="/leads")


SORT_OPTIONS = {
    "lead_potential": Lead.score.desc(),
    "reviews": Lead.review_count.desc().nullslast(),
    "rating": Lead.google_rating.desc().nullslast(),
    "seo_score": AuditResult.score_seo.desc().nullslast(),
    "date": Lead.created_at.desc(),
}

SCORE_RANGES = {
    "0-39": (0, 39),
    "40-59": (40, 59),
    "60-79": (60, 79),
    "80-100": (80, 100),
}

LEGACY_OUTREACH_STATUS_MAP = {
    "follow_up_1": "contacted",
    "follow_up_2": "callback",
    "follow_up_3": "callback",
    "replied": "reviewed",
    "qualified": "reviewed",
    "meeting_booked": "won",
}


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def _normalize_phone(value: str | None) -> str:
    raw = (value or "").strip()
    return "".join(ch for ch in raw if ch.isdigit() or ch == "+")


def _extract_domain(value: str | None) -> str:
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return (parsed.netloc or "").lower().removeprefix("www.")


def _map_legacy_outreach_status(value: str, enabled: bool = True) -> str:
    if not enabled:
        return value
    return LEGACY_OUTREACH_STATUS_MAP.get(value, value)


def build_lead_query_from_args(args):
    query = Lead.query.outerjoin(AuditResult, AuditResult.lead_id == Lead.id)

    text_query = (args.get("q") or "").strip()
    city = (args.get("city") or "").strip()
    status = (args.get("status") or "").strip()
    contact_filter = (args.get("contact") or "").strip()
    review_lt_30 = _truthy(args.get("review_lt_30"))
    rating_missing = _truthy(args.get("rating_missing"))
    impressum_missing = _truthy(args.get("impressum_missing"))
    localbusiness_missing = _truthy(args.get("localbusiness_missing"))
    sort_by = (args.get("sort") or "lead_potential").strip()
    score_ranges = [
        item for item in args.getlist("score_range") if item in SCORE_RANGES
    ]

    if text_query:
        like = f"%{text_query}%"
        query = query.filter(
            or_(
                Lead.company_name.ilike(like),
                Lead.address.ilike(like),
                Lead.website.ilike(like),
            )
        )
    if city:
        query = query.filter(Lead.city.ilike(f"%{city}%"))
    if status:
        query = query.filter(Lead.status == status)

    if contact_filter == "website_missing":
        query = query.filter(or_(Lead.website.is_(None), Lead.website == ""))
    elif contact_filter == "email_missing":
        query = query.filter(or_(Lead.email.is_(None), Lead.email == ""))
    elif contact_filter == "phone_missing":
        query = query.filter(or_(Lead.phone.is_(None), Lead.phone == ""))

    if review_lt_30:
        query = query.filter(or_(Lead.review_count.is_(None), Lead.review_count < 30))
    if rating_missing:
        query = query.filter(Lead.google_rating.is_(None))
    if impressum_missing:
        query = query.filter(Lead.website.isnot(None), Lead.impressum_found.is_(False))

    if localbusiness_missing:
        query = query.filter(
            Lead.audit_results.any(
                AuditResult.issues.any(AuditIssue.category == "structured_data")
            )
        )

    if score_ranges:
        score_conditions = [
            Lead.score.between(SCORE_RANGES[key][0], SCORE_RANGES[key][1])
            for key in score_ranges
        ]
        query = query.filter(or_(*score_conditions))

    sort_clause = SORT_OPTIONS.get(sort_by, SORT_OPTIONS["lead_potential"])
    query = query.order_by(sort_clause, Lead.created_at.desc())

    filters = {
        "q": text_query,
        "city": city,
        "status": status,
        "contact": contact_filter,
        "review_lt_30": review_lt_30,
        "rating_missing": rating_missing,
        "impressum_missing": impressum_missing,
        "localbusiness_missing": localbusiness_missing,
        "sort": sort_by,
        "score_ranges": score_ranges,
    }
    return query.distinct(), filters


@leads_bp.get("")
def leads_list() -> str:
    query, filters = build_lead_query_from_args(request.args)
    leads = query.all()
    statuses = [
        item[0]
        for item in db.session.query(Lead.status).distinct().order_by(Lead.status)
    ]
    return render_template(
        "leads.html",
        leads=leads,
        filters=filters,
        statuses=statuses,
        status_labels=OUTREACH_STATUS_LABELS,
        score_ranges=SCORE_RANGES,
    )


@leads_bp.get("/<int:lead_id>")
@leads_bp.get("/detail/<int:lead_id>")
def lead_detail(lead_id: int) -> str:
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    status_form = StatusForm(status=lead.status)

    latest_audit = (
        AuditResult.query.filter_by(lead_id=lead.id)
        .order_by(AuditResult.created_at.desc())
        .first()
    )
    issue_counts: dict[str, int] = {}
    quick_wins: list[str] = []
    top_sales_arguments: list[str] = []
    if latest_audit:
        issue_counts = {
            severity: count
            for severity, count in (
                db.session.query(AuditIssue.severity, db.func.count(AuditIssue.id))
                .filter(AuditIssue.audit_result_id == latest_audit.id)
                .group_by(AuditIssue.severity)
                .all()
            )
        }
        raw = latest_audit.raw_audit_json or {}
        quick_wins = [
            entry.get("recommendation", "")
            for entry in raw.get("quick_wins", [])
            if entry.get("recommendation")
        ]
        top_sales_arguments = raw.get("top_sales_arguments", []) or []

    score_details = None
    try:
        score_details = json.loads(lead.score_reasons) if lead.score_reasons else None
    except json.JSONDecodeError:
        score_details = None

    email_normalized = _normalize_email(lead.email)
    phone_normalized = _normalize_phone(lead.phone)
    domain = _extract_domain(lead.website)

    opt_out_match = (
        db.session.query(OptOut)
        .filter(
            db.or_(
                db.and_(
                    OptOut.email_normalized.isnot(None),
                    OptOut.email_normalized == email_normalized,
                ),
                db.and_(
                    OptOut.phone_normalized.isnot(None),
                    OptOut.phone_normalized == phone_normalized,
                ),
                db.and_(OptOut.domain.isnot(None), OptOut.domain == domain),
            )
        )
        .order_by(OptOut.created_at.desc())
        .all()
    )

    blacklist_match = (
        db.session.query(Blacklist)
        .filter(Blacklist.active.is_(True))
        .filter(
            db.or_(
                db.and_(
                    Blacklist.entry_type == "email",
                    Blacklist.value_normalized == email_normalized,
                ),
                db.and_(
                    Blacklist.entry_type == "phone",
                    Blacklist.value_normalized == phone_normalized,
                ),
                db.and_(
                    Blacklist.entry_type == "domain",
                    Blacklist.value_normalized == domain,
                ),
            )
        )
        .order_by(Blacklist.created_at.desc())
        .all()
    )

    return render_template(
        "lead_detail.html",
        lead=lead,
        status_form=status_form,
        status_labels=OUTREACH_STATUS_LABELS,
        latest_audit=latest_audit,
        issue_counts=defaultdict(int, issue_counts),
        quick_wins=quick_wins,
        top_sales_arguments=top_sales_arguments,
        score_details=score_details,
        opt_out_match=opt_out_match,
        blacklist_match=blacklist_match,
    )


@leads_bp.post("/<int:lead_id>/status")
def update_status(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    form = StatusForm()
    if form.validate_on_submit():
        selected_status = (form.status.data or "").strip()
        map_legacy = _truthy(request.form.get("map_legacy"))
        mapped_status = _map_legacy_outreach_status(selected_status, enabled=map_legacy)
        if selected_status not in OUTREACH_STATUS_LABELS:
            flash("Ungültiger Status", "error")
            return redirect(url_for("leads.lead_detail", lead_id=lead.id))
        lead.status = mapped_status
        db.session.commit()
        if mapped_status != selected_status:
            flash(
                (
                    f"Legacy-Status '{selected_status}' "
                    f"wurde auf '{mapped_status}' migriert."
                ),
                "info",
            )
        flash("Status aktualisiert", "success")
    else:
        flash("Ungültiger Status", "error")
    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.post("/<int:lead_id>/rerun-audit")
def rerun_audit(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))
    if not lead.website:
        flash("Keine Website vorhanden", "error")
        return redirect(url_for("leads.lead_detail", lead_id=lead.id))

    try:
        audit = audit_website(lead.website, current_app.config["REQUEST_TIMEOUT"])
        lead.site_title = audit.site_title
        lead.meta_description = audit.meta_description
        lead.has_h1 = audit.has_h1
        lead.has_cta = audit.has_cta
        lead.mobile_signals = audit.mobile_signals
        lead.has_contact_info = audit.has_contact_info
        lead.page_load_ms = audit.page_load_ms
        lead.impressum_found = audit.impressum_found
        lead.parser_notes = audit.parser_notes
        lead.checked_pages = audit.checked_pages
        lead.audit_notes = audit.audit_notes
        detected_urls = detect_contact_form_urls(lead)
        lead.contact_form_urls = merge_contact_form_urls(
            lead.contact_form_urls, detected_urls
        )
        if audit.email:
            lead.email = audit.email
        if audit.phone:
            lead.phone = audit.phone
        if audit.owner_name:
            lead.owner_name = audit.owner_name
        if audit.legal_form:
            lead.legal_form = audit.legal_form
        persist_audit_result(lead, audit)
        lead.score, _ = calculate_lead_score(lead)
        lead.score_reasons = json.dumps(
            calculate_lead_score_details(lead), ensure_ascii=False
        )
        db.session.commit()
        flash("Audit erneut durchgeführt", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Audit fehlgeschlagen: {exc}", "error")

    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.post("/<int:lead_id>/drafts")
def create_draft(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    channel = (request.form.get("channel") or "email").strip()[:30]
    subject = (request.form.get("subject") or "").strip()[:255]
    body = (request.form.get("body") or "").strip()
    language = (request.form.get("language") or "de").strip()[:10]
    tone = (request.form.get("tone") or "").strip()[:50]
    if not body:
        flash("Draft-Text darf nicht leer sein", "error")
        return redirect(url_for("leads.lead_detail", lead_id=lead.id))

    draft = OutreachDraft(
        lead_id=lead.id,
        channel=channel,
        subject=subject or None,
        body=body,
        language=language,
        tone=tone or None,
    )
    try:
        with db.session.begin():
            db.session.add(draft)
        flash("Draft erstellt", "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Draft konnte nicht erstellt werden: {exc}", "error")
    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.post("/<int:lead_id>/drafts/contact-form")
def create_contact_form_draft(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    latest_audit = (
        AuditResult.query.filter_by(lead_id=lead.id)
        .order_by(AuditResult.created_at.desc())
        .first()
    )
    detected_urls = detect_contact_form_urls(lead, latest_audit=latest_audit)
    lead.contact_form_urls = merge_contact_form_urls(
        lead.contact_form_urls, detected_urls
    )

    draft_payload = build_contact_form_draft(
        lead=lead, target_urls=lead.contact_form_urls or detected_urls
    )
    draft = OutreachDraft(
        lead_id=lead.id,
        channel="contact_form",
        subject=draft_payload.subject,
        body=draft_payload.body,
        template_key="contact_form_detected_urls",
        meta_json={"target_urls": draft_payload.target_urls, "auto_send": False},
    )
    try:
        db.session.add(draft)
        db.session.commit()
        flash("Kontaktformular-Draft erstellt (kein Versand).", "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Draft konnte nicht erstellt werden: {exc}", "error")
    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.post("/<int:lead_id>/contact-attempts")
def create_contact_attempt(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    attempt = ContactAttempt(
        lead_id=lead.id,
        channel=(request.form.get("channel") or "email").strip()[:30],
        status=(request.form.get("status") or "planned").strip()[:30],
        direction=(request.form.get("direction") or "outbound").strip()[:20],
        subject=(request.form.get("subject") or "").strip()[:255] or None,
        message=(request.form.get("message") or "").strip() or None,
        recipient=(request.form.get("recipient") or "").strip()[:255] or None,
        response_summary=(request.form.get("response_summary") or "").strip() or None,
        attempted_at=datetime.now(UTC),
    )
    try:
        with db.session.begin():
            db.session.add(attempt)
        flash("Kontaktversuch angelegt", "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Kontaktversuch konnte nicht gespeichert werden: {exc}", "error")
    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.post("/<int:lead_id>/phone-note")
def save_phone_note(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    note = (request.form.get("phone_note") or "").strip()
    if not note:
        flash("Telefonnotiz darf nicht leer sein", "error")
        return redirect(url_for("leads.lead_detail", lead_id=lead.id))
    try:
        with db.session.begin():
            attempt = ContactAttempt(
                lead_id=lead.id,
                channel="phone",
                status="note",
                direction="outbound",
                message=note,
                attempted_at=datetime.now(UTC),
            )
            db.session.add(attempt)
        flash("Telefonnotiz gespeichert", "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Telefonnotiz konnte nicht gespeichert werden: {exc}", "error")
    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.post("/<int:lead_id>/callback")
def set_callback_date(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    callback_raw = (request.form.get("callback_at") or "").strip()
    try:
        callback_dt = datetime.fromisoformat(callback_raw)
    except ValueError:
        flash("Ungültiges Callback-Datum", "error")
        return redirect(url_for("leads.lead_detail", lead_id=lead.id))

    try:
        with db.session.begin():
            attempt = ContactAttempt(
                lead_id=lead.id,
                channel="phone",
                status="callback_planned",
                direction="outbound",
                message="Callback geplant",
                attempted_at=callback_dt,
            )
            db.session.add(attempt)
        flash("Callback-Datum gesetzt", "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Callback konnte nicht gespeichert werden: {exc}", "error")
    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.post("/<int:lead_id>/contact-block")
def set_contact_block(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    block_type = (request.form.get("block_type") or "opt_out").strip()
    channel = (request.form.get("channel") or "email").strip()
    reason = (request.form.get("reason") or "").strip()[:255] or None

    email_normalized = _normalize_email(lead.email)
    phone_normalized = _normalize_phone(lead.phone)
    domain = _extract_domain(lead.website)
    try:
        with db.session.begin():
            if block_type == "blacklist":
                entry_type = (request.form.get("entry_type") or "email").strip()
                value_map = {
                    "email": email_normalized,
                    "phone": phone_normalized,
                    "domain": domain,
                }
                value_normalized = value_map.get(entry_type, "")
                if not value_normalized:
                    flash("Kein gültiger Wert für Blacklist gefunden", "error")
                    return redirect(url_for("leads.lead_detail", lead_id=lead.id))
                existing = (
                    db.session.query(Blacklist)
                    .filter_by(entry_type=entry_type, value=value_normalized)
                    .first()
                )
                if existing:
                    existing.active = True
                    existing.reason = reason or existing.reason
                else:
                    db.session.add(
                        Blacklist(
                            entry_type=entry_type,
                            value=value_normalized,
                            value_normalized=value_normalized,
                            reason=reason,
                        )
                    )
            else:
                if not any([email_normalized, phone_normalized, domain]):
                    flash("Keine Kontaktinformationen für Opt-Out vorhanden", "error")
                    return redirect(url_for("leads.lead_detail", lead_id=lead.id))
                db.session.add(
                    OptOut(
                        channel=channel,
                        email=lead.email,
                        email_normalized=email_normalized or None,
                        phone=lead.phone,
                        phone_normalized=phone_normalized or None,
                        domain=domain or None,
                        reason=reason,
                        requested_at=datetime.now(UTC),
                    )
                )
        flash("Kontakt wurde gesperrt", "success")
    except Exception as exc:  # noqa: BLE001
        db.session.rollback()
        flash(f"Sperre konnte nicht gespeichert werden: {exc}", "error")
    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.get("/legacy/<int:lead_id>")
def legacy_redirect(lead_id: int):
    return redirect(url_for("leads.lead_detail", lead_id=lead_id), code=301)
