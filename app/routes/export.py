from __future__ import annotations

from flask import Blueprint

from app.services.export_service import export_leads_csv


export_bp = Blueprint("export", __name__)


@export_bp.get("/export/csv")
def export_csv():
    return export_leads_csv()
