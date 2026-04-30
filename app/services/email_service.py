from __future__ import annotations

import smtplib
from dataclasses import dataclass
from email.message import EmailMessage

from flask import current_app


@dataclass(frozen=True, slots=True)
class EmailSendResult:
    status: str
    provider: str
    recipient: str | None
    subject: str | None
    error_message: str | None = None


def send_outreach_email(
    *, recipient: str, subject: str, body: str
) -> EmailSendResult:
    provider = (
        current_app.config.get("EMAIL_PROVIDER") or "debug"
    ).lower().strip()

    if provider == "debug":
        current_app.logger.info(
            (
                "Debug-E-Mail vorbereitet (kein Versand): "
                "recipient=%s subject=%s body_len=%s"
            ),
            recipient,
            subject,
            len(body or ""),
        )
        return EmailSendResult(
            status="debug",
            provider="debug",
            recipient=recipient,
            subject=subject,
        )

    if provider == "smtp":
        smtp_host = (current_app.config.get("SMTP_HOST") or "").strip()
        smtp_port = int(current_app.config.get("SMTP_PORT") or 587)
        email_from = (current_app.config.get("EMAIL_FROM") or "").strip()
        reply_to = (current_app.config.get("EMAIL_REPLY_TO") or "").strip()
        smtp_username = (current_app.config.get("SMTP_USERNAME") or "").strip()
        smtp_password = (current_app.config.get("SMTP_PASSWORD") or "").strip()
        smtp_use_tls = bool(current_app.config.get("SMTP_USE_TLS", True))
        smtp_use_ssl = bool(current_app.config.get("SMTP_USE_SSL", False))

        if not smtp_host or not smtp_port or not email_from:
            return EmailSendResult(
                status="error",
                provider="smtp",
                recipient=recipient,
                subject=subject,
                error_message=(
                    "SMTP-Konfiguration unvollständig "
                    "(SMTP_HOST/SMTP_PORT/EMAIL_FROM erforderlich)."
                ),
            )

        message = EmailMessage()
        message["From"] = email_from
        message["To"] = recipient
        message["Subject"] = subject
        if reply_to:
            message["Reply-To"] = reply_to
        message.set_content(body or "")

        try:
            if smtp_use_ssl:
                with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
                    if smtp_username:
                        server.login(smtp_username, smtp_password)
                    server.send_message(message)
            else:
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    if smtp_use_tls:
                        server.starttls()
                    if smtp_username:
                        server.login(smtp_username, smtp_password)
                    server.send_message(message)
            return EmailSendResult(
                status="sent",
                provider="smtp",
                recipient=recipient,
                subject=subject,
            )
        except Exception as exc:  # noqa: BLE001
            return EmailSendResult(
                status="error",
                provider="smtp",
                recipient=recipient,
                subject=subject,
                error_message=str(exc),
            )

    return EmailSendResult(
        status="error",
        provider=provider,
        recipient=recipient,
        subject=subject,
        error_message=f"Unbekannter E-Mail-Provider: {provider}",
    )
