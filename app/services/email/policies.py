from __future__ import annotations

import re
from typing import Any

from app.services.email.exceptions import EmailPolicyBlockedError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _attr(obj: Any, name: str, default: Any = None) -> Any:
    return getattr(obj, name, default)


def validate_email_send_allowed(
    lead: Any,
    draft: Any = None,
    *,
    manual_approval: bool = False,
) -> None:
    if not manual_approval:
        raise EmailPolicyBlockedError("manual_approval is required")

    if lead is None:
        raise EmailPolicyBlockedError("lead is required")

    recipient = _attr(lead, "email")
    if not recipient or not _EMAIL_RE.match(str(recipient).strip()):
        raise EmailPolicyBlockedError("valid recipient email is required")

    if draft is not None:
        status = str(_attr(draft, "status", "")).strip().lower()
        if status != "approved":
            raise EmailPolicyBlockedError("draft must be approved")

    outreach_allowed = _attr(lead, "outreach_allowed", None)
    if outreach_allowed is not None and not bool(outreach_allowed):
        raise EmailPolicyBlockedError("lead outreach is not allowed")

    outreach_status = _attr(lead, "outreach_status", None)
    if outreach_status is not None and str(outreach_status).lower() not in {
        "approved",
        "allow",
        "allowed",
        "ok",
    }:
        raise EmailPolicyBlockedError("lead outreach status does not allow sending")

    for block_flag in ("opt_out", "blacklisted", "is_opt_out", "is_blacklisted"):
        flag = _attr(lead, block_flag, None)
        if flag is True:
            raise EmailPolicyBlockedError(f"lead blocked by {block_flag}")

    send_count = _attr(lead, "send_count", None)
    send_limit = _attr(lead, "send_limit", None)
    if (
        send_count is not None
        and send_limit is not None
        and int(send_count) >= int(send_limit)
    ):
        raise EmailPolicyBlockedError("send limit reached")
