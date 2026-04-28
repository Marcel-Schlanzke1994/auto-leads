from app.models import AuditResult, Lead
from app.services.contact_form_service import (
    build_contact_form_draft,
    detect_contact_form_urls,
    merge_contact_form_urls,
)


def test_detect_contact_form_urls_from_checked_pages_and_audit_data():
    lead = Lead(
        company_name="Kontakt GmbH",
        source_query="x",
        website="https://example.com",
        checked_pages=(
            "https://example.com/\n"
            "https://example.com/kontakt\n"
            "https://example.com/impressum"
        ),
        audit_notes="Final URL=https://example.com/contact-form",
    )
    audit = AuditResult(
        checked_url="https://example.com/get-in-touch",
        redirected_url="https://example.com/support",
        raw_audit_json={"link": "https://example.com/contact"},
    )

    urls = detect_contact_form_urls(lead, latest_audit=audit, limit=4)

    assert "https://example.com/kontakt" in urls
    assert "https://example.com/contact-form" in urls
    assert len(urls) <= 4


def test_merge_contact_form_urls_is_additive_without_duplicates():
    merged = merge_contact_form_urls(
        ["https://example.com/kontakt"],
        ["https://example.com/kontakt", "https://example.com/contact"],
    )

    assert merged == ["https://example.com/kontakt", "https://example.com/contact"]


def test_build_contact_form_draft_lists_detected_urls():
    lead = Lead(company_name="Muster AG", source_query="x")

    draft = build_contact_form_draft(
        lead, ["https://example.com/contact", "https://example.com/kontakt"]
    )

    assert draft.subject.startswith("Kontaktformular-Draft")
    assert "https://example.com/contact" in draft.body
    assert draft.target_urls == [
        "https://example.com/contact",
        "https://example.com/kontakt",
    ]
