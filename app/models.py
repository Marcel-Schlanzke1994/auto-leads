from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.extensions import db


class Lead(db.Model):
    __tablename__ = "leads"

    __table_args__ = (
        db.Index(
            "ix_leads_normalized_name_city",
            "normalized_company_name",
            "city_normalized",
        ),
    )

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(255), nullable=False, index=True)
    normalized_company_name = db.Column(db.String(255), index=True)
    industry = db.Column(db.String(120), index=True)
    city = db.Column(db.String(120), index=True)
    city_normalized = db.Column(db.String(120), index=True)
    address = db.Column(db.String(255))

    website = db.Column(db.String(500), index=True)
    domain = db.Column(db.String(255), unique=True, index=True)
    email = db.Column(db.String(255), index=True)
    email_normalized = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(120), index=True)
    phone_normalized = db.Column(db.String(40), index=True)
    owner_name = db.Column(db.String(255))
    legal_form = db.Column(db.String(80))

    place_id = db.Column(db.String(255), unique=True, index=True)
    google_place_id = db.Column(db.String(255), unique=True, index=True)
    google_maps_url = db.Column(db.String(500))
    google_rating = db.Column(db.Float)
    review_count = db.Column(db.Integer)
    categories = db.Column(db.String(500))
    raw_place_json = db.Column(db.JSON)

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
    contact_form_urls = db.Column(db.JSON, nullable=False, default=list)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    audit_results = db.relationship(
        "AuditResult", back_populates="lead", cascade="all, delete-orphan"
    )
    contact_attempts = db.relationship(
        "ContactAttempt", back_populates="lead", cascade="all, delete-orphan"
    )
    outreach_drafts = db.relationship(
        "OutreachDraft", back_populates="lead", cascade="all, delete-orphan"
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
    raw_results_count = db.Column(db.Integer, nullable=False, default=0)
    new_leads_count = db.Column(db.Integer, nullable=False, default=0)
    duplicate_count = db.Column(db.Integer, nullable=False, default=0)
    error_count = db.Column(db.Integer, nullable=False, default=0)
    total_processed = db.Column(db.Integer, nullable=False, default=0)
    filtered_out = db.Column(db.Integer, nullable=False, default=0)

    # Backwards-compatible aliases to avoid immediate breakage in runtime code.
    total_found_raw = db.Column(db.Integer, nullable=False, default=0)
    total_created = db.Column(db.Integer, nullable=False, default=0)
    duplicates_skipped = db.Column(db.Integer, nullable=False, default=0)
    errors = db.Column(db.Integer, nullable=False, default=0)

    current_city = db.Column(db.String(120))
    current_query = db.Column(db.String(255))
    message = db.Column(db.String(500), nullable=False, default="")
    log_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
    started_at = db.Column(
        db.DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    finished_at = db.Column(db.DateTime(timezone=True))

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class AuditResult(db.Model):
    __tablename__ = "audit_results"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(
        db.Integer, db.ForeignKey("leads.id"), nullable=False, index=True
    )

    status = db.Column(db.String(30), nullable=False, default="pending", index=True)

    score_overall = db.Column(db.Float)
    score_performance = db.Column(db.Float)
    score_accessibility = db.Column(db.Float)
    score_best_practices = db.Column(db.Float)
    score_seo = db.Column(db.Float)
    score_content = db.Column(db.Float)
    score_trust = db.Column(db.Float)

    cwv_lcp_ms = db.Column(db.Integer)
    cwv_inp_ms = db.Column(db.Integer)
    cwv_cls = db.Column(db.Float)
    cwv_fcp_ms = db.Column(db.Integer)
    cwv_ttfb_ms = db.Column(db.Integer)

    seo_title = db.Column(db.String(255))
    seo_meta_description = db.Column(db.Text)
    seo_h1_count = db.Column(db.Integer)
    seo_h2_count = db.Column(db.Integer)
    seo_word_count = db.Column(db.Integer)
    seo_canonical_url = db.Column(db.String(500))
    seo_noindex = db.Column(db.Boolean)
    seo_robots_txt_found = db.Column(db.Boolean)
    seo_sitemap_found = db.Column(db.Boolean)

    trust_https = db.Column(db.Boolean)
    trust_impressum_found = db.Column(db.Boolean)
    trust_privacy_found = db.Column(db.Boolean)
    trust_contact_found = db.Column(db.Boolean)

    checked_url = db.Column(db.String(500))
    redirected_url = db.Column(db.String(500))
    page_language = db.Column(db.String(20))
    notes = db.Column(db.Text)

    raw_audit_json = db.Column(db.JSON)
    raw_lighthouse_json = db.Column(db.JSON)
    raw_pagespeed_json = db.Column(db.JSON)
    meta_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    lead = db.relationship("Lead", back_populates="audit_results")
    issues = db.relationship(
        "AuditIssue", back_populates="audit_result", cascade="all, delete-orphan"
    )

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class AuditIssue(db.Model):
    __tablename__ = "audit_issues"

    id = db.Column(db.Integer, primary_key=True)
    audit_result_id = db.Column(
        db.Integer, db.ForeignKey("audit_results.id"), nullable=False, index=True
    )

    severity = db.Column(db.String(20), nullable=False, index=True)
    category = db.Column(db.String(80), nullable=False, index=True)
    code = db.Column(db.String(120), index=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    recommendation = db.Column(db.Text)

    element = db.Column(db.String(255))
    selector = db.Column(db.String(255))
    page_url = db.Column(db.String(500))

    score_impact = db.Column(db.Float)
    weight = db.Column(db.Float)
    is_blocking = db.Column(db.Boolean, nullable=False, default=False)

    raw_issue_json = db.Column(db.JSON)
    meta_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    audit_result = db.relationship("AuditResult", back_populates="issues")

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class ContactAttempt(db.Model):
    __tablename__ = "contact_attempts"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(
        db.Integer, db.ForeignKey("leads.id"), nullable=False, index=True
    )

    channel = db.Column(db.String(30), nullable=False, index=True)
    status = db.Column(db.String(30), nullable=False, default="planned", index=True)
    direction = db.Column(db.String(20), nullable=False, default="outbound", index=True)
    subject = db.Column(db.String(255))
    message = db.Column(db.Text)
    recipient = db.Column(db.String(255), index=True)
    attempted_at = db.Column(db.DateTime(timezone=True))
    response_at = db.Column(db.DateTime(timezone=True))
    response_summary = db.Column(db.Text)
    meta_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    lead = db.relationship("Lead", back_populates="contact_attempts")

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class OutreachDraft(db.Model):
    __tablename__ = "outreach_drafts"

    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(
        db.Integer, db.ForeignKey("leads.id"), nullable=False, index=True
    )

    channel = db.Column(db.String(30), nullable=False, index=True)
    template_key = db.Column(db.String(120), index=True)
    language = db.Column(db.String(10), nullable=False, default="de", index=True)
    tone = db.Column(db.String(50))
    subject = db.Column(db.String(255))
    body = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), nullable=False, default="draft", index=True)
    approved_at = db.Column(db.DateTime(timezone=True))
    sent_at = db.Column(db.DateTime(timezone=True))
    meta_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    lead = db.relationship("Lead", back_populates="outreach_drafts")

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class OptOut(db.Model):
    __tablename__ = "opt_outs"

    id = db.Column(db.Integer, primary_key=True)
    channel = db.Column(db.String(30), nullable=False, index=True)
    email = db.Column(db.String(255), index=True)
    email_normalized = db.Column(db.String(255), index=True)
    phone = db.Column(db.String(40), index=True)
    phone_normalized = db.Column(db.String(40), index=True)
    domain = db.Column(db.String(255), index=True)
    reason = db.Column(db.String(255))
    source = db.Column(db.String(100), nullable=False, default="manual")
    requested_at = db.Column(db.DateTime(timezone=True))
    meta_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Blacklist(db.Model):
    __tablename__ = "blacklists"

    id = db.Column(db.Integer, primary_key=True)
    entry_type = db.Column(db.String(20), nullable=False, index=True)
    value = db.Column(db.String(255), nullable=False, index=True)
    value_normalized = db.Column(db.String(255), index=True)
    reason = db.Column(db.String(255))
    source = db.Column(db.String(100), nullable=False, default="manual")
    active = db.Column(db.Boolean, nullable=False, default=True, index=True)
    expires_at = db.Column(db.DateTime(timezone=True))
    meta_json = db.Column(db.JSON)

    created_at = db.Column(
        db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    __table_args__ = (
        db.UniqueConstraint(
            "entry_type", "value", name="uq_blacklists_entry_type_value"
        ),
    )

    def to_dict(self) -> dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
