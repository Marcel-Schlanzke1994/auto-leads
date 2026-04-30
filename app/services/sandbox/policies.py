from dataclasses import dataclass

from app.services.sandbox.limits import (
    MAX_ANALYSIS_SECONDS,
    MAX_PAGES_PER_LEAD,
    MAX_REDIRECTS,
    MAX_RESPONSE_BYTES,
    MAX_SCREENSHOTS_PER_LEAD,
    REQUEST_TIMEOUT_SECONDS,
)


@dataclass(frozen=True, slots=True)
class SandboxPolicy:
    request_timeout_seconds: int = REQUEST_TIMEOUT_SECONDS
    max_redirects: int = MAX_REDIRECTS
    max_pages_per_lead: int = MAX_PAGES_PER_LEAD
    max_screenshots_per_lead: int = MAX_SCREENSHOTS_PER_LEAD
    max_response_bytes: int = MAX_RESPONSE_BYTES
    max_analysis_seconds: int = MAX_ANALYSIS_SECONDS


DEFAULT_SANDBOX_POLICY = SandboxPolicy()
