from __future__ import annotations

import json
from collections import defaultdict

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

from app.models import AuditIssue, AuditResult, Lead
from app.services.lead_score_service import (
    calculate_lead_score,
    calculate_lead_score_details,
)
from app.services.website_audit_service import audit_website, persist_audit_result
from auto_leads.extensions import db
from auto_leads.forms import StatusForm


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


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


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

    return render_template(
        "lead_detail.html",
        lead=lead,
        status_form=status_form,
        latest_audit=latest_audit,
        issue_counts=defaultdict(int, issue_counts),
        quick_wins=quick_wins,
        top_sales_arguments=top_sales_arguments,
        score_details=score_details,
    )


@leads_bp.post("/<int:lead_id>/status")
def update_status(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))

    form = StatusForm()
    if form.validate_on_submit():
        lead.status = form.status.data
        db.session.commit()
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


@leads_bp.get("/legacy/<int:lead_id>")
def legacy_redirect(lead_id: int):
    return redirect(url_for("leads.lead_detail", lead_id=lead_id), code=301)
