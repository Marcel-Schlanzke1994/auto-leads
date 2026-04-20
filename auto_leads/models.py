from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .extensions import db


class Lead(db.Model):
    __tablename__ = "leads"

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False, index=True)
    industry = db.Column(db.String(120), index=True)
    city = db.Column(db.String(120), index=True)
    address = db.Column(db.String(255))
    website = db.Column(db.String(500), index=True)
    email = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(120), index=True)
    owner_name = db.Column(db.String(255))
    legal_form = db.Column(db.String(80))

    google_place_id = db.Column(db.String(255), unique=True, index=True)
    google_rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    categories = db.Column(db.String(500))
    source = db.Column(db.String(100), nullable=False, default="google_places")
    source_query = db.Column(db.String(255), nullable=False, index=True)

    status = db.Column(db.String(30), nullable=False, default="new", index=True)
    score = db.Column(db.Integer, nullable=False, default=0)
    score_reasons = db.Column(db.Text, nullable=False, default="")

    site_title = db.Column(db.String(255))
    meta_description = db.Column(db.Text)
    has_h1 = db.Column(db.Boolean, nullable=False, default=False)
    has_cta = db.Column(db.Boolean, nullable=False, default=False)
    mobile_signals = db.Column(db.Boolean, nullable=False, default=False)
    has_contact_info = db.Column(db.Boolean, nullable=False, default=False)
    page_load_ms = db.Column(db.Integer)
    impressum_found = db.Column(db.Boolean, nullable=False, default=False)
    audit_notes = db.Column(db.Text, nullable=False, default="")
    parser_notes = db.Column(db.Text, nullable=False, default="")
    checked_pages = db.Column(db.Text, nullable=False, default="")

    created_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "company_name": self.company_name,
            "industry": self.industry,
            "city": self.city,
            "address": self.address,
            "website": self.website,
            "email": self.email,
            "phone": self.phone,
            "owner_name": self.owner_name,
            "legal_form": self.legal_form,
            "google_place_id": self.google_place_id,
            "google_rating": self.google_rating,
            "review_count": self.review_count,
            "categories": self.categories,
            "source": self.source,
            "source_query": self.source_query,
            "status": self.status,
            "score": self.score,
            "score_reasons": self.score_reasons,
            "site_title": self.site_title,
            "meta_description": self.meta_description,
            "has_h1": self.has_h1,
            "has_cta": self.has_cta,
            "mobile_signals": self.mobile_signals,
            "has_contact_info": self.has_contact_info,
            "page_load_ms": self.page_load_ms,
            "impressum_found": self.impressum_found,
            "audit_notes": self.audit_notes,
            "parser_notes": self.parser_notes,
            "checked_pages": self.checked_pages,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SearchJob(db.Model):
    __tablename__ = "search_jobs"

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(200), nullable=False)
    cities = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="queued")
    total = db.Column(db.Integer, nullable=False, default=0)
    processed = db.Column(db.Integer, nullable=False, default=0)
    created = db.Column(db.Integer, nullable=False, default=0)
    skipped_duplicates = db.Column(db.Integer, nullable=False, default=0)
    errors = db.Column(db.Integer, nullable=False, default=0)
    message = db.Column(db.String(500), nullable=False, default="")
    started_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    finished_at = db.Column(db.DateTime(timezone=True))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "keyword": self.keyword,
            "cities": self.cities,
            "status": self.status,
            "total": self.total,
            "processed": self.processed,
            "created": self.created,
            "skipped_duplicates": self.skipped_duplicates,
            "errors": self.errors,
            "message": self.message,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
        }
