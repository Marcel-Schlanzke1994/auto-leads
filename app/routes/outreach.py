from __future__ import annotations

from flask import Blueprint, render_template, request
from sqlalchemy import func, select

from app.extensions import db
from app.forms import OUTREACH_STATUS_LABELS
from app.models import Blacklist, ContactAttempt, Lead, OptOut, OutreachDraft

outreach_bp = Blueprint("outreach", __name__, url_prefix="/outreach")


def _status_sort_key(value: str) -> tuple[int, str]:
    options = list(OUTREACH_STATUS_LABELS.keys())
    if value in options:
        return (options.index(value), value)
    return (len(options), value)


@outreach_bp.get("")
def outreach_overview() -> str:
    status_filter = (request.args.get("status") or "").strip()
    score_min_raw = (request.args.get("score_min") or "").strip()
    city_filter = (request.args.get("city") or "").strip()
    industry_filter = (request.args.get("industry") or "").strip()

    query = Lead.query

    if status_filter:
        query = query.filter(Lead.status == status_filter)

    score_min = None
    if score_min_raw:
        try:
            score_min = int(score_min_raw)
            query = query.filter(Lead.score >= score_min)
        except ValueError:
            score_min = None

    if city_filter:
        query = query.filter(Lead.city.ilike(f"%{city_filter}%"))

    if industry_filter:
        query = query.filter(Lead.industry.ilike(f"%{industry_filter}%"))

    filtered_query = query.order_by(Lead.score.desc(), Lead.created_at.desc())
    filtered_lead_ids = select(filtered_query.with_entities(Lead.id).subquery().c.id)

    status_counts_raw = (
        query.with_entities(Lead.status, func.count(Lead.id))
        .group_by(Lead.status)
        .order_by(Lead.status)
        .all()
    )
    status_counts = sorted(status_counts_raw, key=lambda row: _status_sort_key(row[0]))

    hot_leads = (
        filtered_query.filter(Lead.score >= 70)
        .filter(~Lead.contact_attempts.any())
        .limit(20)
        .all()
    )

    drafts_for_review = (
        OutreachDraft.query.join(Lead, OutreachDraft.lead_id == Lead.id)
        .filter(OutreachDraft.status == "draft")
        .filter(Lead.id.in_(filtered_lead_ids))
        .order_by(OutreachDraft.created_at.desc())
        .limit(20)
        .all()
    )

    callback_items = (
        ContactAttempt.query.join(Lead, ContactAttempt.lead_id == Lead.id)
        .filter(ContactAttempt.status == "callback_planned")
        .filter(Lead.id.in_(filtered_lead_ids))
        .order_by(
            ContactAttempt.scheduled_for.asc().nullslast(),
            ContactAttempt.attempted_at.asc().nullslast(),
        )
        .limit(30)
        .all()
    )

    opt_out_items = OptOut.query.order_by(OptOut.created_at.desc()).limit(30).all()

    blacklist_items = (
        Blacklist.query.filter(Blacklist.active.is_(True))
        .order_by(Blacklist.created_at.desc())
        .limit(30)
        .all()
    )

    available_statuses = [
        item[0]
        for item in db.session.query(Lead.status).distinct().order_by(Lead.status).all()
    ]

    context = {
        "status_filter": status_filter,
        "score_min": score_min_raw,
        "city_filter": city_filter,
        "industry_filter": industry_filter,
    }

    return render_template(
        "outreach.html",
        status_counts=status_counts,
        hot_leads=hot_leads,
        drafts_for_review=drafts_for_review,
        callback_items=callback_items,
        opt_out_items=opt_out_items,
        blacklist_items=blacklist_items,
        available_statuses=available_statuses,
        status_labels=OUTREACH_STATUS_LABELS,
        filters=context,
    )
