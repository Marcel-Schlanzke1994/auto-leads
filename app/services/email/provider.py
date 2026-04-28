from __future__ import annotations

import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Mapping

from app.services.email.exceptions import EmailProviderConfigurationError


@dataclass(slots=True)
class EmailMessage:
    to: str
    subject: str
    body: str
    reply_to: str | None = None
    from_email: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class EmailSendResult:
    provider: str
    status: str
    message_id: str | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class EmailProvider(ABC):
    @abstractmethod
    def send(self, message: EmailMessage) -> EmailSendResult:
        raise NotImplementedError


def _is_truthy(value: str | None) -> bool:
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def get_email_provider(config: Mapping[str, Any] | None = None) -> EmailProvider:
    cfg = config or os.environ
    provider_name = str(cfg.get("EMAIL_PROVIDER", "debug")).strip().lower() or "debug"

    if provider_name == "debug":
        from app.services.email.debug_provider import DebugEmailProvider

        return DebugEmailProvider()

    if provider_name == "cloudflare":
        if not _is_truthy(str(cfg.get("CLOUDFLARE_EMAIL_PROVIDER_ENABLED", "false"))):
            raise EmailProviderConfigurationError(
                "Cloudflare email provider requested but feature flag is disabled."
            )
        from app.services.email.cloudflare_provider import CloudflareEmailProvider

        return CloudflareEmailProvider(config=cfg)

    raise EmailProviderConfigurationError(f"Unknown email provider: {provider_name}")
