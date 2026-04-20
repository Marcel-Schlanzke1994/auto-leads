from __future__ import annotations

from auto_leads.models import Lead


def calculate_lead_score(lead: Lead) -> tuple[int, list[str]]:
    score = 10
    reasons = ["Basis-Score +10"]

    if (lead.review_count or 0) < 30:
        score += 16
        reasons.append("Wenig Reviews (<30) +16")
    elif (lead.review_count or 0) < 100:
        score += 8
        reasons.append("Moderate Reviews (<100) +8")

    if lead.google_rating is None:
        score += 7
        reasons.append("Google-Rating fehlt +7")
    elif lead.google_rating < 4.2:
        score += 12
        reasons.append("Google-Sternebewertung niedrig (<4.2) +12")

    if not lead.website:
        score += 20
        reasons.append("Website fehlt +20")
    else:
        reasons.append("Website vorhanden +0")

    if not lead.email:
        score += 8
        reasons.append("E-Mail fehlt +8")

    if not lead.phone:
        score += 8
        reasons.append("Keine Telefonnummer +8")

    if lead.website and not lead.impressum_found:
        score += 14
        reasons.append("Impressum nicht gefunden +14")
    elif lead.impressum_found:
        reasons.append("Impressum gefunden +0")

    if not lead.meta_description:
        score += 5
        reasons.append("Meta Description fehlt +5")
    if not lead.has_h1:
        score += 5
        reasons.append("H1 fehlt +5")
    if not lead.has_cta:
        score += 8
        reasons.append("CTA fehlt +8")

    if lead.page_load_ms and lead.page_load_ms > 2500:
        score += 7
        reasons.append("Langsame Website (>2.5s) +7")

    return min(score, 100), reasons
