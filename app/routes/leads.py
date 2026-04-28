from __future__ import annotations

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)

from app.models import Lead
from app.services.lead_score_service import calculate_lead_score
from app.services.website_audit_service import audit_website
from auto_leads.extensions import db
from auto_leads.forms import StatusForm


leads_bp = Blueprint("leads", __name__, url_prefix="/leads")


@leads_bp.get("")
def leads_list() -> str:
    leads = Lead.query.order_by(Lead.score.desc(), Lead.created_at.desc()).all()
    query = (request.args.get("q") or "").strip().lower()
    if query:
        leads = [lead for lead in leads if query in (lead.company_name or "").lower()]
    return render_template("leads.html", leads=leads, query=query)


@leads_bp.get("/<int:lead_id>")
@leads_bp.get("/detail/<int:lead_id>")
def lead_detail(lead_id: int) -> str:
    lead = db.session.get(Lead, lead_id)
    if not lead:
        flash("Lead nicht gefunden", "error")
        return redirect(url_for("leads.leads_list"))
    status_form = StatusForm(status=lead.status)
    return render_template("lead_detail.html", lead=lead, status_form=status_form)


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
        lead.score, reasons = calculate_lead_score(lead)
        lead.score_reasons = "\n".join(reasons)
        db.session.commit()
        flash("Audit erneut durchgeführt", "success")
    except Exception as exc:  # noqa: BLE001
        flash(f"Audit fehlgeschlagen: {exc}", "error")

    return redirect(url_for("leads.lead_detail", lead_id=lead.id))


@leads_bp.get("/legacy/<int:lead_id>")
def legacy_redirect(lead_id: int):
    return redirect(url_for("leads.lead_detail", lead_id=lead_id), code=301)
