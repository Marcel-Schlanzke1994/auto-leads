from __future__ import annotations

from flask import Blueprint, abort, jsonify, render_template, request

from app.models import SearchJob
from app.extensions import db

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_bp.get("")
def list_jobs() -> str:
    jobs = SearchJob.query.order_by(SearchJob.id.desc()).all()
    return render_template("jobs.html", jobs=jobs)


@jobs_bp.get("/<int:job_id>")
def job_detail(job_id: int) -> str:
    job = db.session.get(SearchJob, job_id)
    if not job:
        abort(404)
    return render_template("job_detail.html", job=job)


@jobs_bp.get("/<int:job_id>/json")
def job_detail_json(job_id: int):
    job = db.session.get(SearchJob, job_id)
    if not job:
        return jsonify({"error": "not found"}), 404

    payload = job.to_dict()
    payload["events"] = job.log_json or []
    payload["events_count"] = len(payload["events"])
    return jsonify(payload)


@jobs_bp.get("/<int:job_id>/progress")
def job_progress_poll(job_id: int):
    job = db.session.get(SearchJob, job_id)
    if not job:
        return jsonify({"error": "not found"}), 404

    since = request.args.get("since", default=0, type=int)
    since = max(0, since)
    events = list(job.log_json or [])
    new_events = events[since:]
    return jsonify(
        {
            "job_id": job.id,
            "status": job.status,
            "message": job.message,
            "current_city": job.current_city,
            "current_query": job.current_query,
            "total_created": job.total_created,
            "total_processed": job.total_processed,
            "total_found_raw": job.total_found_raw,
            "duplicates_skipped": job.duplicates_skipped,
            "errors": job.errors,
            "filtered_out": job.filtered_out,
            "target_count": min(job.target_count, 1000),
            "events_total": len(events),
            "events": new_events,
        }
    )
