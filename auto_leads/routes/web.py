from __future__ import annotations

import csv
import io

from flask import (
    Blueprint,
    Response,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from auto_leads.extensions import db, limiter
from auto_leads.forms import SearchForm, StatusForm
from auto_leads.models import Lead, SearchJob
from auto_leads.services.scoring import calculate_lead_score
from auto_leads.services.search_runner import start_search_job

web_bp = Blueprint("web", __name__)


@web_bp.get("/")
def dashboard() -> str:
    leads = Lead.query.order_by(Lead.score.desc(), Lead.created_at.desc()).all()
    stats = {
        "total": len(leads),
        "new": sum(1 for lead_item in leads if lead_item.status == "new"),
        "high_score": sum(1 for lead_item in leads if lead_item.score >= 70),
        "with_website": sum(1 for lead_item in leads if lead_item.website),
        "with_email": sum(1 for lead_item in leads if lead_item.email),
        "with_phone": sum(1 for lead_item in leads if lead_item.phone),
        "impressum_found": sum(1 for lead_item in leads if lead_item.impressum_found),
        "with_google_rating": sum(
            1 for lead_item in leads if lead_item.google_rating is not None
        ),
    }
    latest_job = SearchJob.query.order_by(SearchJob.id.desc()).first()
    return render_template(
        "dashboard.html", leads=leads, stats=stats, latest_job=latest_job
    )


@web_bp.route("/search", methods=["GET", "POST"])
@limiter.limit("15/hour")
def search() -> str:
    form = SearchForm()
    if form.validate_on_submit():
        cities = [c.strip() for c in form.cities.data.split(",") if c.strip()]
        job = start_search_job(
            current_app._get_current_object(),
            keyword=form.keyword.data.strip(),
            cities=cities,
            target_count=form.target_count.data or 1000,
        )
        flash(f"Suchjob #{job.id} gestartet", "success")
        return redirect(url_for("web.dashboard"))

    if request.method == "POST":
        flash("Bitte Eingaben prüfen.", "error")
    return render_template("search.html", form=form)


@web_bp.get("/lead/<int:lead_id>")
def lead_detail(lead_id: int) -> str:
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("web.dashboard"))
    status_form = StatusForm(status=lead.status)
    return render_template("lead_detail.html", lead=lead, status_form=status_form)


@web_bp.post("/lead/<int:lead_id>/status")
def update_status(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("web.dashboard"))

    form = StatusForm()
    if form.validate_on_submit():
        lead.status = form.status.data
        db.session.commit()
        flash("Status aktualisiert", "success")
    else:
        flash("Ungültiger Status", "error")
    return redirect(url_for("web.lead_detail", lead_id=lead.id))


@web_bp.post("/lead/<int:lead_id>/rerun-audit")
def rerun_audit(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("web.dashboard"))

    from auto_leads.services.audit import audit_website

    if not lead.website:
        flash("Keine Website vorhanden", "error")
        return redirect(url_for("web.lead_detail", lead_id=lead.id))

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
        lead.score, reasons = calculate_lead_score(lead)
        lead.score_reasons = "\n".join(reasons)
        db.session.commit()
        flash("Audit erneut durchgeführt", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Audit fehlgeschlagen: {exc}", "error")

    return redirect(url_for("web.lead_detail", lead_id=lead.id))


@web_bp.get("/export/csv")
def export_csv() -> Response:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "id",
            "company_name",
            "city",
            "address",
            "website",
            "email",
            "phone",
            "owner_name",
            "legal_form",
            "google_place_id",
            "google_rating",
            "review_count",
            "score",
            "score_reasons",
            "status",
            "source_query",
            "impressum_found",
            "created_at",
        ]
    )

    for lead in Lead.query.order_by(Lead.created_at.desc()).all():
        writer.writerow(
            [
                lead.id,
                lead.company_name,
                lead.city,
                lead.address,
                lead.website,
                lead.email,
                lead.phone,
                lead.owner_name,
                lead.legal_form,
                lead.google_place_id,
                lead.google_rating,
                lead.review_count,
                lead.score,
                lead.score_reasons,
                lead.status,
                lead.source_query,
                lead.impressum_found,
                lead.created_at.isoformat() if lead.created_at else "",
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=leads.csv"
    return response
