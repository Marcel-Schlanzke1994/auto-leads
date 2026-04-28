from __future__ import annotations

import csv
import io
from datetime import UTC, datetime
from urllib.parse import urlparse

from flask import Response

from app.extensions import db
from app.models import AuditIssue, AuditResult, Blacklist, Lead, OptOut
from app.services.duplicate_service import normalize_company_name


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
    "contact_status",
    "last_contact_at",
    "next_callback_at",
    "outreach_allowed",
    "draft_count",
    "attempt_count",
    "created_at",
]


def _normalize_email(value: str | None) -> str:
    return (value or "").strip().lower()


def _normalize_phone(value: str | None) -> str:
    raw = (value or "").strip()
    return "".join(ch for ch in raw if ch.isdigit() or ch == "+")


def _extract_domain(value: str | None) -> str:
    if not value:
        return ""
    parsed = urlparse(value if "://" in value else f"https://{value}")
    return (parsed.netloc or "").lower().removeprefix("www.")


def _latest_audit(lead: Lead) -> AuditResult | None:
    if not lead.audit_results:
        return None
    return max(lead.audit_results, key=lambda item: item.created_at)


def _is_outreach_blocked(lead: Lead) -> bool:
    email_normalized = _normalize_email(lead.email)
    phone_normalized = _normalize_phone(lead.phone)
    domain = _extract_domain(lead.website)
    normalized_company = normalize_company_name(lead.company_name)

    opt_out_exists = (
        db.session.query(OptOut.id)
        .filter(
            db.or_(
                db.and_(
                    OptOut.email_normalized.isnot(None),
                    OptOut.email_normalized == email_normalized,
                ),
                db.and_(
                    OptOut.phone_normalized.isnot(None),
                    OptOut.phone_normalized == phone_normalized,
                ),
                db.and_(OptOut.domain.isnot(None), OptOut.domain == domain),
                db.and_(
                    OptOut.company_name_normalized.isnot(None),
                    OptOut.company_name_normalized == normalized_company,
                ),
            )
        )
        .first()
        is not None
    )
    if opt_out_exists:
        return True

    blacklist_exists = (
        db.session.query(Blacklist.id)
        .filter(Blacklist.active.is_(True))
        .filter(
            db.or_(
                db.and_(
                    Blacklist.entry_type == "email",
                    Blacklist.value_normalized == email_normalized,
                ),
                db.and_(
                    Blacklist.entry_type == "phone",
                    Blacklist.value_normalized == phone_normalized,
                ),
                db.and_(
                    Blacklist.entry_type == "domain",
                    Blacklist.value_normalized == domain,
                ),
                db.and_(
                    Blacklist.entry_type == "company",
                    Blacklist.value_normalized == normalized_company,
                ),
            )
        )
        .first()
        is not None
    )
    return blacklist_exists


def _contact_metadata(lead: Lead) -> tuple[str, str, str, bool, int, int]:
    attempts = list(lead.contact_attempts or [])
    drafts = list(lead.outreach_drafts or [])

    attempt_count = len(attempts)
    draft_count = len(drafts)
    outreach_allowed = not _is_outreach_blocked(lead)

    contact_timestamps = [
        ts
        for attempt in attempts
        for ts in (attempt.attempted_at, attempt.response_at)
        if ts is not None
    ]
    last_contact_at = max(contact_timestamps) if contact_timestamps else None

    callback_attempts = [
        attempt
        for attempt in attempts
        if attempt.status == "callback_planned"
        and (attempt.scheduled_for is not None or attempt.attempted_at is not None)
    ]
    next_callback_at = None
    if callback_attempts:
        now_aware = datetime.now(UTC)
        now_naive = now_aware.replace(tzinfo=None)

        def _callback_at(attempt):
            return attempt.scheduled_for or attempt.attempted_at

        future_callbacks = [
            _callback_at(attempt)
            for attempt in callback_attempts
            if (
                _callback_at(attempt) >= now_aware
                if _callback_at(attempt).tzinfo is not None
                else _callback_at(attempt) >= now_naive
            )
        ]
        if future_callbacks:
            next_callback_at = min(future_callbacks)
        else:
            next_callback_at = max(_callback_at(a) for a in callback_attempts)

    latest_attempt = None
    if attempts:
        latest_attempt = max(
            attempts,
            key=lambda item: item.attempted_at or item.created_at,
        )

    if not outreach_allowed:
        contact_status = "blocked"
    elif next_callback_at is not None:
        contact_status = "callback_planned"
    elif latest_attempt is not None:
        contact_status = latest_attempt.status
    elif draft_count > 0:
        contact_status = "drafted"
    else:
        contact_status = "new"

    return (
        contact_status,
        last_contact_at.isoformat() if last_contact_at else "",
        next_callback_at.isoformat() if next_callback_at else "",
        outreach_allowed,
        draft_count,
        attempt_count,
    )


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

        (
            contact_status,
            last_contact_at,
            next_callback_at,
            outreach_allowed,
            draft_count,
            attempt_count,
        ) = _contact_metadata(lead)

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
                contact_status,
                last_contact_at,
                next_callback_at,
                outreach_allowed,
                draft_count,
                attempt_count,
                lead.created_at.isoformat() if lead.created_at else "",
            ]
        )

    response = Response(output.getvalue(), mimetype="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response
