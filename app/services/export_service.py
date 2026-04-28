from __future__ import annotations

import csv
import io

from flask import Response

from app.models import AuditIssue, AuditResult, Lead


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
    "seo_score",
    "score_overall",
    "score_performance",
    "score_accessibility",
    "score_best_practices",
    "seo_noindex",
    "seo_robots_txt_found",
    "seo_sitemap_found",
    "trust_https",
    "trust_impressum_found",
    "trust_privacy_found",
    "trust_contact_found",
    "cwv_lcp_ms",
    "cwv_inp_ms",
    "cwv_cls",
    "cwv_fcp_ms",
    "cwv_ttfb_ms",
    "critical_issues_count",
    "warning_issues_count",
    "opportunity_issues_count",
    "quick_win_issues_count",
    "top_3_sales_arguments",
    "created_at",
]


def _latest_audit(lead: Lead) -> AuditResult | None:
    if not lead.audit_results:
        return None
    return max(lead.audit_results, key=lambda item: item.created_at)


def export_leads_csv(leads: list[Lead], filename: str = "leads.csv") -> Response:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(CSV_HEADERS)

    for lead in leads:
        latest_audit = _latest_audit(lead)
        issue_counts = {
            "critical": 0,
            "warning": 0,
            "opportunity": 0,
            "quick_win": 0,
        }
        top_3_sales_arguments = ""

        if latest_audit:
            raw_audit = latest_audit.raw_audit_json or {}
            top_3_sales_arguments = " | ".join(
                (raw_audit.get("top_sales_arguments") or [])[:3]
            )
            grouped = (
                AuditIssue.query.with_entities(
                    AuditIssue.severity,
                    AuditIssue.id,
                )
                .filter(AuditIssue.audit_result_id == latest_audit.id)
                .all()
            )
            for issue in grouped:
                if issue.severity in issue_counts:
                    issue_counts[issue.severity] += 1

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
                latest_audit.score_seo if latest_audit else None,
                latest_audit.score_overall if latest_audit else None,
                latest_audit.score_performance if latest_audit else None,
                latest_audit.score_accessibility if latest_audit else None,
                latest_audit.score_best_practices if latest_audit else None,
                latest_audit.seo_noindex if latest_audit else None,
                latest_audit.seo_robots_txt_found if latest_audit else None,
                latest_audit.seo_sitemap_found if latest_audit else None,
                latest_audit.trust_https if latest_audit else None,
                latest_audit.trust_impressum_found if latest_audit else None,
                latest_audit.trust_privacy_found if latest_audit else None,
                latest_audit.trust_contact_found if latest_audit else None,
                latest_audit.cwv_lcp_ms if latest_audit else None,
                latest_audit.cwv_inp_ms if latest_audit else None,
                latest_audit.cwv_cls if latest_audit else None,
                latest_audit.cwv_fcp_ms if latest_audit else None,
                latest_audit.cwv_ttfb_ms if latest_audit else None,
                issue_counts["critical"],
                issue_counts["warning"],
                issue_counts["opportunity"],
                issue_counts["quick_win"],
                top_3_sales_arguments,
                lead.created_at.isoformat() if lead.created_at else "",
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
