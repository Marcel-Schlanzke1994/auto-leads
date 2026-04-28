from __future__ import annotations

from flask import Blueprint, request

from app.models import Lead
from app.routes.leads import build_lead_query_from_args
from app.services.export_service import export_leads_csv


export_bp = Blueprint("export", __name__)


@export_bp.get("/export/csv")
def export_csv():
    leads = Lead.query.order_by(Lead.created_at.desc()).all()
    return export_leads_csv(leads, filename="leads_all.csv")


@export_bp.get("/export/csv/high-potential")
def export_csv_high_potential():
    min_score = request.args.get("min_score", type=int) or 70
    leads = (
        Lead.query.filter(Lead.score >= min_score)
        .order_by(Lead.score.desc(), Lead.created_at.desc())
        .all()
    )
    return export_leads_csv(leads, filename=f"leads_high_potential_{min_score}.csv")


@export_bp.get("/export/csv/filtered")
def export_csv_filtered():
    query, _ = build_lead_query_from_args(request.args)
    leads = query.all()
    return export_leads_csv(leads, filename="leads_filtered.csv")
