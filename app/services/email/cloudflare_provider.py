from __future__ import annotations

import uuid
from typing import Any, Mapping

from app.services.email.exceptions import EmailProviderConfigurationError
from app.services.email.provider import EmailMessage, EmailProvider, EmailSendResult


class CloudflareEmailProvider(EmailProvider):
    name = "cloudflare"

    def __init__(self, config: Mapping[str, Any]):
        self._enabled = str(
            config.get("CLOUDFLARE_EMAIL_PROVIDER_ENABLED", "false")
        ).lower() in {
            "1",
            "true",
            "yes",
            "on",
        }
        self._token = str(config.get("CLOUDFLARE_EMAIL_API_TOKEN", "")).strip()
        self._from_email = str(config.get("CLOUDFLARE_EMAIL_FROM", "")).strip()

        if not self._enabled:
            raise EmailProviderConfigurationError(
                "Cloudflare email provider is disabled."
            )
        if not self._token:
            raise EmailProviderConfigurationError("Missing CLOUDFLARE_EMAIL_API_TOKEN.")
        if not self._from_email:
            raise EmailProviderConfigurationError("Missing CLOUDFLARE_EMAIL_FROM.")

    def send(self, message: EmailMessage) -> EmailSendResult:
        message_id = f"cf-stub-{uuid.uuid4()}"
        return EmailSendResult(
            provider=self.name,
            status="sent",
            message_id=message_id,
            metadata={
                "mode": "stub",
                "note": (
                    "Cloudflare provider is prepared as adapter; real API wiring "
                    "intentionally not active in phase 8."
                ),
                "to": message.to,
                "from_email": message.from_email or self._from_email,
            },
        )
