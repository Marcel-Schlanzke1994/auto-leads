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

from app.models import Lead, OutreachDraft, SearchJob
from app.services.search_runner_service import start_search_job
from app.forms import SearchForm
from app.extensions import db, limiter


dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/", methods=["GET", "POST"])
@dashboard_bp.route("/dashboard", methods=["GET", "POST"])
def dashboard() -> str:
    form = SearchForm()
    default_cities = ", ".join(current_app.config.get("SEARCH_DEFAULT_CITIES", []))
    max_target = int(current_app.config.get("SEARCH_MAX_TARGET_COUNT", 1000))
    if request.method == "GET" and not form.cities.data:
        form.cities.data = default_cities
    if request.method == "GET" and not form.target_count.data:
        form.target_count.data = max_target
    if form.validate_on_submit():
        cities = [city.strip() for city in form.cities.data.split(",") if city.strip()]
        job = start_search_job(
            current_app._get_current_object(),
            keyword=form.keyword.data.strip(),
            cities=cities,
            target_count=form.target_count.data or max_target,
        )
        flash(f"Suchjob #{job.id} gestartet", "success")
        return redirect(url_for("dashboard.dashboard"))

    if request.method == "POST":
        flash("Bitte Eingaben prüfen.", "error")

    leads = Lead.query.order_by(Lead.score.desc(), Lead.created_at.desc()).all()
    latest_outreach_drafts = (
        OutreachDraft.query.options(db.joinedload(OutreachDraft.lead))
        .order_by(OutreachDraft.created_at.desc())
        .limit(20)
        .all()
    )
    stats = {
        "total": len(leads),
        "outreach_drafts": OutreachDraft.query.count(),
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
        "dashboard.html",
        form=form,
        max_target=max_target,
        default_cities=default_cities,
        stats=stats,
        latest_job=latest_job,
        latest_outreach_drafts=latest_outreach_drafts,
        leads=leads[:10],
    )


@dashboard_bp.route("/search", methods=["GET", "POST"])
@limiter.limit("15/hour")
def search_compat() -> str:
    return dashboard()
