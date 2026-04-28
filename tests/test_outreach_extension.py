from datetime import UTC, datetime

from app.extensions import db
from app.models import AuditIssue, AuditResult, Blacklist, ContactAttempt, Lead, OptOut
from app.services.outreach_draft_service import generate_outreach_draft


def _create_lead(**overrides):
    defaults = {
        "company_name": "Outreach GmbH",
        "source_query": "seo köln",
        "website": "https://outreach.example",
        "email": "kontakt@outreach.example",
        "email_normalized": "kontakt@outreach.example",
        "status": "new",
    }
    defaults.update(overrides)
    return Lead(**defaults)


def test_draft_generation_blocked_for_opt_out(client, app):
    with app.app_context():
        lead = _create_lead()
        db.session.add(lead)
        db.session.flush()
        db.session.add(
            OptOut(
                channel="email",
                email=lead.email,
                email_normalized=lead.email_normalized,
            )
        )
        db.session.commit()

        result = generate_outreach_draft(lead=lead, channel="email")

        assert result.blocked is True
        assert result.status == "blocked"
        assert result.error_code == "outreach_blocked"
        assert "Opt-out" in (result.error_message or "")


def test_draft_generation_blocked_for_blacklist(client, app):
    with app.app_context():
        lead = _create_lead()
        db.session.add(lead)
        db.session.flush()
        db.session.add(
            Blacklist(
                entry_type="domain",
                value="outreach.example",
                value_normalized="outreach.example",
                active=True,
            )
        )
        db.session.commit()

        result = generate_outreach_draft(lead=lead, channel="email")

        assert result.blocked is True
        assert result.status == "blocked"
        assert result.error_code == "outreach_blocked"
        assert "Blacklist" in (result.error_message or "")


def test_draft_generation_blocked_for_company_opt_out(app):
    with app.app_context():
        lead = _create_lead(company_name="Musterfirma GmbH")
        db.session.add(lead)
        db.session.flush()
        db.session.add(
            OptOut(
                channel="email",
                company_name=lead.company_name,
                company_name_normalized="musterfirma",
            )
        )
        db.session.commit()

        result = generate_outreach_draft(lead=lead, channel="email")

        assert result.blocked is True
        assert result.status == "blocked"
        assert result.error_code == "outreach_blocked"
        assert "Unternehmen" in (result.error_message or "")


def test_set_contact_block_adds_company_opt_out_and_blacklist(client, app):
    with app.app_context():
        lead = _create_lead(company_name="Firmenname GmbH")
        db.session.add(lead)
        db.session.commit()
        lead_id = lead.id

    response_opt_out = client.post(
        f"/leads/{lead_id}/contact-block",
        data={
            "block_type": "opt_out",
            "channel": "all",
            "opt_out_company": "1",
            "reason": "Kein Outreach",
        },
    )
    assert response_opt_out.status_code == 302

    response_blacklist = client.post(
        f"/leads/{lead_id}/contact-block",
        data={
            "block_type": "blacklist",
            "blacklist_company": "1",
            "reason": "Do not contact",
        },
    )
    assert response_blacklist.status_code == 302

    with app.app_context():
        opt_out = OptOut.query.order_by(OptOut.id.desc()).first()
        assert opt_out is not None
        assert opt_out.company_name == "Firmenname GmbH"
        assert opt_out.company_name_normalized == "firmenname"

        blacklist = Blacklist.query.filter_by(entry_type="company").first()
        assert blacklist is not None
        assert blacklist.value_normalized == "firmenname"
        assert blacklist.company_name == "Firmenname GmbH"


def test_contact_attempt_creation_persists_required_fields(app):
    with app.app_context():
        lead = _create_lead()
        db.session.add(lead)
        db.session.flush()

        attempt = ContactAttempt(
            lead_id=lead.id,
            channel="email",
            status="sent",
            direction="outbound",
            subject="Kurzer Impuls",
            message="Hallo Team",
            recipient="kontakt@outreach.example",
            attempted_at=datetime.now(UTC),
        )
        db.session.add(attempt)
        db.session.commit()

        saved = ContactAttempt.query.filter_by(lead_id=lead.id).one()
        assert saved.channel == "email"
        assert saved.status == "sent"
        assert saved.recipient == "kontakt@outreach.example"
        assert saved.attempted_at is not None


def test_lead_status_change_route_updates_status(client, app):
    with app.app_context():
        lead = _create_lead(status="new")
        db.session.add(lead)
        db.session.commit()
        lead_id = lead.id

    response = client.post(
        f"/leads/{lead_id}/status",
        data={"status": "meeting_booked"},
    )

    assert response.status_code == 302

    with app.app_context():
        refreshed = db.session.get(Lead, lead_id)
        assert refreshed is not None
        assert refreshed.status == "meeting_booked"


def test_csv_export_contains_outreach_fields(client, app):
    with app.app_context():
        db.session.add(_create_lead())
        db.session.commit()

    response = client.get("/export/csv")

    assert response.status_code == 200
    header = response.get_data(as_text=True).splitlines()[0].split(",")
    assert "contact_status" in header
    assert "last_contact_at" in header
    assert "next_callback_at" in header
    assert "outreach_allowed" in header
    assert "draft_count" in header
    assert "attempt_count" in header


def test_draft_generator_uses_audit_data(app):
    with app.app_context():
        lead = _create_lead(company_name="Audit GmbH")
        db.session.add(lead)
        db.session.flush()

        audit = AuditResult(
            lead_id=lead.id,
            score_performance=0.67,
            score_seo=0.58,
            cwv_lcp_ms=2450,
            seo_h1_count=0,
            seo_meta_description="",
            created_at=datetime.now(UTC),
        )
        db.session.add(audit)
        db.session.flush()

        issue = AuditIssue(
            audit_result_id=audit.id,
            severity="high",
            category="seo",
            title="Zu lange Title-Tags",
        )
        db.session.add(issue)
        db.session.commit()

        result = generate_outreach_draft(
            lead=lead,
            channel="email",
            audit_result=audit,
            audit_issues=[issue],
        )

        assert result.status == "ok"
        assert result.blocked is False
        assert result.subject is not None
        assert "Performance-Score" in (result.body or "")
        assert "SEO-Score" in (result.body or "")
        assert "Zu lange Title-Tags" in (result.body or "")
