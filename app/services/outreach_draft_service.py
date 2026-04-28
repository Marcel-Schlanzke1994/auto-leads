from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from app.models import AuditIssue, AuditResult, Blacklist, Lead, OptOut
from app.services.duplicate_service import (
    normalize_company_name,
    normalize_domain,
    normalize_email,
)

SUPPORTED_CHANNELS = {"email", "contact_form", "phone_script"}
DEFAULT_LANGUAGE = "de"
FIXED_SIGNATURE = (
    "Freundliche Grüße\n" "Marcel Schlanzke\n" "auto-leads\n" "kontakt@auto-leads.de"
)


@dataclass(slots=True)
class BlockCheckResult:
    blocked: bool
    status: str
    reason: str | None = None
    matched_field: str | None = None
    matched_value: str | None = None


@dataclass(slots=True)
class DraftGenerationResult:
    status: str
    channel: str
    blocked: bool
    error_code: str | None = None
    error_message: str | None = None
    subject: str | None = None
    body: str | None = None


def check_outreach_block(lead: Lead, channel: str) -> BlockCheckResult:
    normalized_email = normalize_email(lead.email)
    normalized_domain = normalize_domain(lead.website) or normalize_domain(lead.domain)
    normalized_company = normalize_company_name(lead.company_name)

    if normalized_email:
        opt_out_by_email = (
            OptOut.query.filter(OptOut.email_normalized == normalized_email)
            .filter(OptOut.channel.in_([channel, "all"]))
            .first()
        )
        if opt_out_by_email:
            return BlockCheckResult(
                blocked=True,
                status="blocked",
                reason="Opt-out für E-Mail vorhanden",
                matched_field="email",
                matched_value=normalized_email,
            )

    if normalized_domain:
        opt_out_by_domain = (
            OptOut.query.filter(OptOut.domain == normalized_domain)
            .filter(OptOut.channel.in_([channel, "all"]))
            .first()
        )
        if opt_out_by_domain:
            return BlockCheckResult(
                blocked=True,
                status="blocked",
                reason="Opt-out für Domain vorhanden",
                matched_field="domain",
                matched_value=normalized_domain,
            )

    if normalized_company:
        opt_out_by_company = (
            OptOut.query.filter(OptOut.company_name_normalized == normalized_company)
            .filter(OptOut.channel.in_([channel, "all"]))
            .first()
        )
        if opt_out_by_company:
            return BlockCheckResult(
                blocked=True,
                status="blocked",
                reason="Opt-out für Unternehmen vorhanden",
                matched_field="company",
                matched_value=normalized_company,
            )

    blacklist_query = Blacklist.query.filter(Blacklist.active.is_(True)).filter(
        (Blacklist.expires_at.is_(None)) | (Blacklist.expires_at > datetime.now(UTC))
    )

    if normalized_email:
        email_hit = blacklist_query.filter(
            Blacklist.entry_type == "email",
            Blacklist.value_normalized == normalized_email,
        ).first()
        if email_hit:
            return BlockCheckResult(
                blocked=True,
                status="blocked",
                reason="Blacklist-Eintrag für E-Mail vorhanden",
                matched_field="email",
                matched_value=normalized_email,
            )

    if normalized_domain:
        domain_hit = blacklist_query.filter(
            Blacklist.entry_type == "domain",
            Blacklist.value_normalized == normalized_domain,
        ).first()
        if domain_hit:
            return BlockCheckResult(
                blocked=True,
                status="blocked",
                reason="Blacklist-Eintrag für Domain vorhanden",
                matched_field="domain",
                matched_value=normalized_domain,
            )

    if normalized_company:
        company_hit = blacklist_query.filter(
            Blacklist.entry_type == "company",
            Blacklist.value_normalized == normalized_company,
        ).first()
        if company_hit:
            return BlockCheckResult(
                blocked=True,
                status="blocked",
                reason="Blacklist-Eintrag für Unternehmen vorhanden",
                matched_field="company",
                matched_value=normalized_company,
            )

    return BlockCheckResult(blocked=False, status="ok")


def generate_outreach_draft(
    *,
    lead: Lead,
    channel: str,
    audit_result: AuditResult | None = None,
    audit_issues: list[AuditIssue] | None = None,
) -> DraftGenerationResult:
    if channel not in SUPPORTED_CHANNELS:
        return DraftGenerationResult(
            status="error",
            channel=channel,
            blocked=False,
            error_code="unsupported_channel",
            error_message=f"Kanal '{channel}' wird nicht unterstützt.",
        )

    block_result = check_outreach_block(lead=lead, channel=channel)
    if block_result.blocked:
        details = (
            f"{block_result.reason} "
            f"({block_result.matched_field}: {block_result.matched_value})"
        )
        return DraftGenerationResult(
            status="blocked",
            channel=channel,
            blocked=True,
            error_code="outreach_blocked",
            error_message=details,
        )

    subject, body = _build_channel_draft(
        lead=lead,
        channel=channel,
        audit_result=audit_result,
        audit_issues=audit_issues or [],
    )
    return DraftGenerationResult(
        status="ok",
        channel=channel,
        blocked=False,
        subject=subject,
        body=body,
    )


def _build_channel_draft(
    *,
    lead: Lead,
    channel: str,
    audit_result: AuditResult | None,
    audit_issues: list[AuditIssue],
) -> tuple[str | None, str]:
    personalization = _build_personalization(lead, audit_result, audit_issues)
    company = lead.company_name or "Ihr Unternehmen"

    if channel == "email":
        subject = f"Kurzer Website-Impuls für {company}"
        body = (
            f"Hallo {company}-Team,\n\n"
            "ich habe mir Ihre Website kurz angesehen und ein paar "
            "konkrete Potenziale gefunden.\n"
            f"{personalization}\n\n"
            "Wenn Sie möchten, bereiten wir daraus eine priorisierte "
            "30-Tage-Maßnahmenliste vor.\n\n"
            f"{FIXED_SIGNATURE}"
        )
        return subject, body

    if channel == "contact_form":
        body = (
            f"Guten Tag {company},\n\n"
            "beim Kurz-Audit Ihrer Website sind uns Optimierungschancen aufgefallen:\n"
            f"{personalization}\n\n"
            "Gerne senden wir Ihnen eine kompakte Priorisierung per E-Mail.\n\n"
            f"{FIXED_SIGNATURE}"
        )
        return None, body

    phone_script = (
        f"Hallo, hier ist Marcel Schlanzke von auto-leads. "
        f"Ich rufe wegen {company} an. "
        "Wir haben einen kurzen Website-Check durchgeführt und 2-3 "
        "schnelle Hebel identifiziert: "
        f"{_inline_personalization(personalization)}. "
        "Darf ich Ihnen die Prioritätenliste an kontakt@auto-leads.de senden?"
    )
    return None, phone_script


def _build_personalization(
    lead: Lead,
    audit_result: AuditResult | None,
    audit_issues: list[AuditIssue],
) -> str:
    if not audit_result and not audit_issues:
        return _fallback_personalization(lead)

    hints: list[str] = []

    if audit_result and audit_result.score_performance is not None:
        hints.append(
            "- Performance-Score bei ca. "
            f"{round(audit_result.score_performance * 100)}/100"
        )

    if audit_result and audit_result.score_seo is not None:
        hints.append(f"- SEO-Score bei ca. {round(audit_result.score_seo * 100)}/100")

    if audit_result and audit_result.cwv_lcp_ms:
        hints.append(f"- LCP liegt bei rund {audit_result.cwv_lcp_ms} ms")

    if audit_result and audit_result.seo_h1_count == 0:
        hints.append("- Auf der Seite fehlt eine klare H1-Überschrift")

    if audit_result and audit_result.seo_meta_description in (None, ""):
        hints.append("- Meta-Description fehlt oder ist unvollständig")

    high_issues = [
        issue for issue in audit_issues if issue.severity in {"high", "critical"}
    ]
    for issue in high_issues[:3]:
        hints.append(f"- {issue.title}")

    if not hints:
        return _fallback_personalization(lead)

    return "\n".join(hints)


def _fallback_personalization(lead: Lead) -> str:
    company = lead.company_name or "Ihr Unternehmen"
    return (
        f"- Wir sehen bei {company} Potenzial bei Ladezeit, Sichtbarkeit "
        "und Conversion-Pfaden\n"
        "- Wir können kurzfristig Quick Wins priorisieren und umsetzbar dokumentieren"
    )


def _inline_personalization(personalization: str) -> str:
    parts = [
        part.strip().lstrip("- ")
        for part in personalization.splitlines()
        if part.strip()
    ]
    return "; ".join(parts[:3])
