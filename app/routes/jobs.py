from __future__ import annotations

from flask import Blueprint, abort, render_template

from app.models import SearchJob


jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_bp.get("")
def list_jobs() -> str:
    jobs = SearchJob.query.order_by(SearchJob.id.desc()).all()
    return render_template("jobs.html", jobs=jobs)


@jobs_bp.get("/<int:job_id>")
def job_detail(job_id: int) -> str:
    job = SearchJob.query.get(job_id)
    if not job:
        abort(404)
    return render_template("job_detail.html", job=job)
