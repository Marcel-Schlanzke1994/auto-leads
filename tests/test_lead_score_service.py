import json

from app.models import Lead
from app.services.lead_score_service import (
    calculate_lead_score,
    calculate_lead_score_details,
)


def test_calculates_subscores_and_overall_score():
    lead = Lead(
        company_name="Subscore GmbH",
        source_query="q",
        review_count=8,
        google_rating=3.8,
        website="https://example.org",
        email="",
        phone=None,
        has_h1=False,
        has_cta=False,
        meta_description="",
        impressum_found=False,
        page_load_ms=3200,
        mobile_signals=False,
        has_contact_info=False,
    )

    score, reason_lines = calculate_lead_score(lead)
    details = calculate_lead_score_details(lead)

    assert score == details["lead_potential_score"]
    assert set(details["subscores"]) == {
        "reputation",
        "website_presence",
        "contact",
        "content",
        "technical",
    }
    assert all(0 <= subscore <= 100 for subscore in details["subscores"].values())
    assert any("RATING_LOW" in item for item in reason_lines)


def test_critical_issues_are_separated_from_subscores():
    lead = Lead(
        company_name="Blocker GmbH",
        source_query="q",
        website=None,
        impressum_found=False,
        has_contact_info=False,
    )

    details = calculate_lead_score_details(lead)
    critical_rule_ids = {item["rule_id"] for item in details["critical_issues"]}

    assert "WEBSITE_MISSING" in critical_rule_ids
    assert details["lead_potential_score"] > 0


def test_rule_explanations_are_machine_readable_json_payload(app):
    lead = Lead(company_name="JSON GmbH", source_query="q", review_count=0)

    payload = calculate_lead_score_details(lead)
    encoded = json.dumps(payload)
    decoded = json.loads(encoded)

    assert isinstance(decoded["rules"], list)
    assert {"rule_id", "weight", "finding", "triggered"}.issubset(decoded["rules"][0])


def test_web_perf_rules_are_additive_and_score_capped():
    from datetime import UTC, datetime

    from app.models import AuditResult

    lead = Lead(
        company_name="Perf GmbH",
        source_query="q",
        website="https://example.org",
        mobile_signals=False,
    )
    audit = AuditResult(
        created_at=datetime.now(UTC),
        raw_pagespeed_json={
            "web_perf": {
                "performance_score": 40,
                "uses_compression": False,
                "render_blocking_risk": "high",
                "image_optimization_risk": "high",
                "mobile_performance_risk": "high",
            }
        },
    )
    lead.audit_results = [audit]

    details = calculate_lead_score_details(lead)
    ids = {rule["rule_id"] for rule in details["rules"] if rule["triggered"]}
    assert "WEB_PERF_SCORE_LOW" in ids
    assert 0 <= details["lead_potential_score"] <= 100
