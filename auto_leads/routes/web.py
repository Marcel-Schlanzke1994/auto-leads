from __future__ import annotations

from flask import Blueprint

from app.routes.dashboard import dashboard
from app.routes.export import export_csv
from app.routes.leads import lead_detail, rerun_audit, update_status

web_bp = Blueprint("web", __name__)


@web_bp.route("/search", methods=["GET", "POST"])
def search():
    return dashboard()


@web_bp.get("/lead/<int:lead_id>")
def lead_detail_legacy(lead_id: int):
    return lead_detail(lead_id)


@web_bp.post("/lead/<int:lead_id>/status")
def update_status_legacy(lead_id: int):
    return update_status(lead_id)


@web_bp.post("/lead/<int:lead_id>/rerun-audit")
def rerun_audit_legacy(lead_id: int):
    return rerun_audit(lead_id)


@web_bp.get("/export/csv")
def export_csv_legacy():
    return export_csv()
