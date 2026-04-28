from __future__ import annotations

import csv
import io

from flask import Response

from app.models import Lead


CSV_HEADERS = [
    "id",
    "company_name",
    "city",
    "address",
    "website",
    "email",
    "phone",
    "owner_name",
    "legal_form",
    "google_place_id",
    "google_rating",
    "review_count",
    "score",
    "score_reasons",
    "status",
    "source_query",
    "impressum_found",
    "created_at",
]


def export_leads_csv() -> Response:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)
    for lead in Lead.query.order_by(Lead.created_at.desc()).all():
        writer.writerow(
            [
                lead.id,
                lead.company_name,
                lead.city,
                lead.address,
                lead.website,
                lead.email,
                lead.phone,
                lead.owner_name,
                lead.legal_form,
                lead.google_place_id,
                lead.google_rating,
                lead.review_count,
                lead.score,
                lead.score_reasons,
                lead.status,
                lead.source_query,
                lead.impressum_found,
                lead.created_at.isoformat() if lead.created_at else "",
            ]
        )
    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = "attachment; filename=leads.csv"
    return response
