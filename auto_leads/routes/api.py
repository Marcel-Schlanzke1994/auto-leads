from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from auto_leads.extensions import db, limiter
from auto_leads.models import Lead, SearchJob
from auto_leads.services.search_runner import start_search_job

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.get("/leads")
def list_leads():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return jsonify([lead.to_dict() for lead in leads])


@api_bp.get("/leads/<int:lead_id>")
def get_lead(lead_id: int):
    lead = db.session.get(Lead, lead_id)
    if not lead:
        return jsonify({"error": "not found"}), 404
    return jsonify(lead.to_dict())


@api_bp.post("/search/start")
@limiter.limit("10/hour")
def api_search_start():
    payload = request.get_json(silent=True) or {}
    keyword = str(payload.get("keyword") or "").strip()
    cities_raw = str(payload.get("cities") or "").strip()
    if not keyword or not cities_raw:
        return jsonify({"error": "keyword and cities are required"}), 400

    cities = [c.strip() for c in cities_raw.split(",") if c.strip()]
    job = start_search_job(current_app._get_current_object(), keyword, cities)
    return jsonify({"job_id": job.id, "status": job.status}), 202


@api_bp.get("/search/progress")
def api_search_progress():
    job_id = request.args.get("job_id", type=int)
    if not job_id:
        latest = SearchJob.query.order_by(SearchJob.id.desc()).first()
        if not latest:
            return jsonify({"error": "no jobs"}), 404
        return jsonify(latest.to_dict())

    job = db.session.get(SearchJob, job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    return jsonify(job.to_dict())
