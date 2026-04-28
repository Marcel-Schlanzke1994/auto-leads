from __future__ import annotations

from functools import wraps

from flask import Blueprint, current_app, jsonify, request

from app.extensions import db, limiter
from app.models import Lead, SearchJob
from app.services.search_runner_service import start_search_job

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _require_api_token(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        header_name = str(current_app.config.get("API_AUTH_HEADER", "X-API-Key"))
        expected_token = str(current_app.config.get("API_AUTH_TOKEN") or "").strip()

        if not expected_token:
            return jsonify({"error": "api auth token is not configured"}), 503

        provided_token = str(request.headers.get(header_name) or "").strip()
        if provided_token != expected_token:
            return jsonify({"error": "unauthorized"}), 401

        return view(*args, **kwargs)

    return wrapped


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
@_require_api_token
@limiter.limit("5/minute;30/hour")
def api_search_start():
    if not request.is_json:
        return jsonify({"error": "json body required"}), 400

    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "json object required"}), 400

    keyword = str(payload.get("keyword") or "").strip()
    cities_raw = str(payload.get("cities") or "").strip()
    target_count_raw = payload.get("target_count")
    target_count_fallback = 1000
    try:
        target_count = int(
            target_count_fallback if target_count_raw is None else target_count_raw
        )
    except (ValueError, TypeError):
        return jsonify({"error": "target_count must be an integer"}), 400

    if not keyword or len(keyword) > 120 or not cities_raw:
        return jsonify({"error": "keyword and cities are required"}), 400

    cities = [c.strip() for c in cities_raw.split(",") if c.strip()]
    if not cities or len(cities) > 25:
        return jsonify({"error": "cities must contain between 1 and 25 values"}), 400

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
