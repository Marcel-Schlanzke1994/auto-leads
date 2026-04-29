from __future__ import annotations


class EmailProviderConfigurationError(RuntimeError):
    """Raised when an email provider is misconfigured."""


class EmailPolicyBlockedError(PermissionError):
    """Raised when email sending is blocked by policy."""
