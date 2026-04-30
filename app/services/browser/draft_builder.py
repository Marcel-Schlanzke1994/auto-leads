from __future__ import annotations

from app.services.outreach_draft_service import FIXED_SIGNATURE


def build_contact_form_message_draft(company_name: str, improvement_hint: str) -> str:
    company = company_name or "Ihr Team"
    hint = improvement_hint or "Wir sehen Potenzial bei Performance und Nutzerführung."
    return (
        f"Guten Tag {company},\n\n"
        "bei einer kurzen Analyse Ihrer Website sind uns konkrete "
        "Verbesserungen aufgefallen. "
        f"Ein Beispiel: {hint}\n\n"
        "Gerne senden wir Ihnen eine kompakte, priorisierte Empfehlung "
        "für schnelle SEO- und UX-Gewinne.\n\n"
        f"{FIXED_SIGNATURE}"
    )
