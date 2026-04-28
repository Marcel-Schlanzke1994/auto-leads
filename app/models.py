from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from auto_leads.extensions import db


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
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class SearchJob(db.Model):
    __tablename__ = "search_jobs"

    id = db.Column(db.Integer, primary_key=True)
    keyword = db.Column(db.String(200), nullable=False)
    cities = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="queued")
    target_count = db.Column(db.Integer, nullable=False, default=1000)
    total_found_raw = db.Column(db.Integer, nullable=False, default=0)
    total_processed = db.Column(db.Integer, nullable=False, default=0)
    total_created = db.Column(db.Integer, nullable=False, default=0)
    duplicates_skipped = db.Column(db.Integer, nullable=False, default=0)
    filtered_out = db.Column(db.Integer, nullable=False, default=0)
    errors = db.Column(db.Integer, nullable=False, default=0)
    current_city = db.Column(db.String(120))
    current_query = db.Column(db.String(255))
    message = db.Column(db.String(500), nullable=False, default="")
    started_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    finished_at = db.Column(db.DateTime(timezone=True))

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
