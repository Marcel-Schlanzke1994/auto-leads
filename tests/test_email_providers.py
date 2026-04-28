from __future__ import annotations

import pytest

from app.services.email import (
    EmailMessage,
    EmailPolicyBlockedError,
    EmailProvider,
    EmailProviderConfigurationError,
    get_email_provider,
    validate_email_send_allowed,
)


def test_debug_provider_returns_preview() -> None:
    provider = get_email_provider({"EMAIL_PROVIDER": "debug"})
    result = provider.send(
        EmailMessage(to="test@example.com", subject="S", body="Body")
    )
    assert result.provider == "debug"
    assert result.status == "preview"
    assert result.metadata["preview"]["to"] == "test@example.com"


def test_default_provider_is_debug() -> None:
    provider = get_email_provider({})
    assert provider.__class__.__name__ == "DebugEmailProvider"


def test_cloudflare_provider_requires_feature_flag() -> None:
    with pytest.raises(EmailProviderConfigurationError):
        get_email_provider(
            {
                "EMAIL_PROVIDER": "cloudflare",
                "CLOUDFLARE_EMAIL_PROVIDER_ENABLED": "false",
            }
        )


def test_policy_blocks_without_manual_approval() -> None:
    lead = type("Lead", (), {"email": "allowed@example.com"})()
    with pytest.raises(EmailPolicyBlockedError):
        validate_email_send_allowed(lead, manual_approval=False)


def test_policy_blocks_unapproved_draft() -> None:
    lead = type("Lead", (), {"email": "allowed@example.com"})()
    draft = type("Draft", (), {"status": "draft"})()
    with pytest.raises(EmailPolicyBlockedError):
        validate_email_send_allowed(lead, draft, manual_approval=True)


def test_policy_blocks_outreach_not_allowed() -> None:
    lead = type(
        "Lead", (), {"email": "allowed@example.com", "outreach_allowed": False}
    )()
    with pytest.raises(EmailPolicyBlockedError):
        validate_email_send_allowed(lead, manual_approval=True)


def test_policy_blocks_opt_out() -> None:
    lead = type("Lead", (), {"email": "allowed@example.com", "opt_out": True})()
    with pytest.raises(EmailPolicyBlockedError):
        validate_email_send_allowed(lead, manual_approval=True)


def test_policy_blocks_blacklist() -> None:
    lead = type("Lead", (), {"email": "allowed@example.com", "blacklisted": True})()
    with pytest.raises(EmailPolicyBlockedError):
        validate_email_send_allowed(lead, manual_approval=True)


def test_policy_allows_explicitly_allowed() -> None:
    lead = type(
        "Lead",
        (),
        {
            "email": "allowed@example.com",
            "outreach_allowed": True,
            "outreach_status": "approved",
            "opt_out": False,
            "blacklisted": False,
        },
    )()
    draft = type("Draft", (), {"status": "approved"})()
    validate_email_send_allowed(lead, draft, manual_approval=True)


def test_provider_interface_has_no_bulk_methods() -> None:
    assert hasattr(EmailProvider, "send")
    assert not hasattr(EmailProvider, "send_many")
    assert not hasattr(EmailProvider, "send_bulk")
    assert not hasattr(EmailProvider, "send_all")
