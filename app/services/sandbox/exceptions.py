class SandboxPolicyError(ValueError):
    """Base error for sandbox policy violations."""


class UnsafeUrlError(SandboxPolicyError):
    """Raised when a URL fails validation."""


class PrivateNetworkBlockedError(UnsafeUrlError):
    """Raised when URL host resolves to a private/internal network."""


class SandboxLimitError(SandboxPolicyError):
    """Raised when a sandbox limit would be exceeded."""
