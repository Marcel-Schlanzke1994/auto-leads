from __future__ import annotations

from app.services.email.provider import EmailMessage, EmailProvider, EmailSendResult


class DebugEmailProvider(EmailProvider):
    name = "debug"

    def send(self, message: EmailMessage) -> EmailSendResult:
        return EmailSendResult(
            provider=self.name,
            status="preview",
            metadata={
                "preview": {
                    "to": message.to,
                    "subject": message.subject,
                    "body": message.body,
                    "reply_to": message.reply_to,
                    "from_email": message.from_email,
                    "metadata": message.metadata,
                }
            },
        )
