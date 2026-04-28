from __future__ import annotations

from flask import Blueprint, current_app, jsonify, request

from auto_leads.extensions import db, limiter
from app.models import Lead, SearchJob
from app.services.search_runner_service import start_search_job

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
    target_count = int(payload.get("target_count") or 1000)

    if not keyword or not cities_raw:
        return jsonify({"error": "keyword and cities are required"}), 400

    cities = [c.strip() for c in cities_raw.split(",") if c.strip()]
    max_target = int(current_app.config.get("SEARCH_MAX_TARGET_COUNT", 1000))
    bounded_target = max(1, min(target_count, max_target))
    job = start_search_job(
        current_app._get_current_object(),
        keyword,
        cities,
        target_count=bounded_target,
    )
    return (
        jsonify(
            {"job_id": job.id, "status": job.status, "target_count": bounded_target}
        ),
        202,
    )


@api_bp.get("/search/jobs/<int:job_id>")
def api_search_job_detail(job_id: int):
    job = db.session.get(SearchJob, job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    payload = job.to_dict()
    payload["events"] = job.log_json or []
    payload["events_count"] = len(payload["events"])
    return jsonify(payload)


@api_bp.get("/search/progress")
def api_search_progress():
    job_id = request.args.get("job_id", type=int)
    since = max(0, request.args.get("since", default=0, type=int))

    if not job_id:
        latest = SearchJob.query.order_by(SearchJob.id.desc()).first()
        if not latest:
            return jsonify({"error": "no jobs"}), 404
        payload = latest.to_dict()
        payload["events"] = (latest.log_json or [])[since:]
        payload["events_total"] = len(latest.log_json or [])
        return jsonify(payload)

    job = db.session.get(SearchJob, job_id)
    if not job:
        return jsonify({"error": "not found"}), 404
    payload = job.to_dict()
    payload["events"] = (job.log_json or [])[since:]
    payload["events_total"] = len(job.log_json or [])
    return jsonify(payload)
