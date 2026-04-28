from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from app.models import AuditIssue as AuditIssueModel
from app.models import AuditResult as AuditResultModel
from app.models import Lead
from app.services.crawler_service import crawl_domain_pages
from app.services.extraction_service import extract_company_profile
from app.services.pagespeed_service import analyze_pagespeed, extract_page_load_ms
from app.services.seo_check_service import CheckResult, analyze_seo, run_all_seo_checks
from app.services.website_fetcher import fetch_website
from app.extensions import db


@dataclass(slots=True)
class AuditResult:
    site_title: str | None
    meta_description: str | None
    has_h1: bool
    has_cta: bool
    mobile_signals: bool
    has_contact_info: bool
    page_load_ms: int | None
    impressum_found: bool
    email: str | None
    phone: str | None
    owner_name: str | None
    legal_form: str | None
    parser_notes: str
    checked_pages: str
    audit_notes: str
    critical_issues: list[dict]
    warnings: list[dict]
    opportunities: list[dict]
    quick_wins: list[dict]
    top_sales_arguments: list[str]
    raw_pagespeed: dict


def audit_website(url: str, timeout: float) -> AuditResult:
    session = requests.Session()
    fetch = fetch_website(url, timeout, session=session)
    seo = analyze_seo(fetch.body)
    soup = BeautifulSoup(fetch.body, "html.parser")
    crawl = crawl_domain_pages(fetch.url, soup, timeout, session)

    combined_text = "\n".join(
        [fetch.body, crawl.combined_text, "\n".join(crawl.checked_pages)]
    )
    profile = extract_company_profile(combined_text)
    page_speed = analyze_pagespeed(fetch.url, fetch, timeout)
    seo_checks = run_all_seo_checks(
        fetch.body, _checks_with_link_status(crawl), urlparse(fetch.url).hostname or ""
    )

    critical_issues = _map_checks(seo_checks, ["high"], passed=False)
    warnings = _map_checks(seo_checks, ["medium"], passed=False)
    opportunities = _map_checks(seo_checks, ["low"], passed=False)
    quick_wins = [
        item
        for item in warnings
        if item["category"]
        in {"meta_description_present", "cta_presence", "whatsapp_hint", "social_hint"}
    ]

    parser_notes = [
        "Impressum gefunden" if crawl.impressum_found else "Impressum nicht gefunden",
        "E-Mail gefunden" if profile.email else "Keine E-Mail",
        "Telefon gefunden" if profile.phone else "Kein Telefon",
    ]
    audit_notes = [
        f"Homepage status={fetch.status_code}",
        f"Final URL={fetch.url}",
        f"Redirects={len(fetch.redirect_history)}",
        f"Crawler checked={len(crawl.checked_pages)}",
        f"Pagespeed source={page_speed['source']}",
    ]

    sales_arguments = _build_sales_arguments(
        critical_issues, warnings, page_speed, profile
    )

    return AuditResult(
        site_title=seo.site_title,
        meta_description=seo.meta_description,
        has_h1=seo.has_h1,
        has_cta=seo.has_cta,
        mobile_signals=seo.mobile_signals,
        has_contact_info=bool(profile.email or profile.phone),
        page_load_ms=extract_page_load_ms(fetch),
        impressum_found=crawl.impressum_found,
        email=profile.email,
        phone=profile.phone,
        owner_name=profile.owner_name,
        legal_form=profile.legal_form,
        parser_notes="\n".join(parser_notes),
        checked_pages="\n".join(crawl.checked_pages),
        audit_notes="\n".join(audit_notes),
        critical_issues=critical_issues,
        warnings=warnings,
        opportunities=opportunities,
        quick_wins=quick_wins,
        top_sales_arguments=sales_arguments,
        raw_pagespeed=page_speed,
    )


def persist_audit_result(lead: Lead, audit: AuditResult) -> AuditResultModel:
    detail = AuditResultModel(
        lead=lead,
        status="done",
        score_overall=_score_overall(audit),
        score_performance=audit.raw_pagespeed.get("performance_score"),
        score_accessibility=audit.raw_pagespeed.get("accessibility_score"),
        score_best_practices=audit.raw_pagespeed.get("best_practices_score"),
        score_seo=audit.raw_pagespeed.get("seo_score"),
        score_content=70.0,
        score_trust=100.0 if audit.impressum_found else 45.0,
        cwv_lcp_ms=audit.raw_pagespeed.get("lcp_ms"),
        cwv_fcp_ms=audit.raw_pagespeed.get("fcp_ms"),
        cwv_ttfb_ms=audit.raw_pagespeed.get("ttfb_ms"),
        seo_title=audit.site_title,
        seo_meta_description=audit.meta_description,
        seo_h1_count=1 if audit.has_h1 else 0,
        seo_h2_count=None,
        seo_word_count=None,
        trust_https="Final URL=https://" in audit.audit_notes,
        trust_impressum_found=audit.impressum_found,
        trust_privacy_found=(
            "privacy" in audit.checked_pages.lower()
            or "datenschutz" in audit.checked_pages.lower()
        ),
        trust_contact_found=(
            "kontakt" in audit.checked_pages.lower()
            or "contact" in audit.checked_pages.lower()
        ),
        checked_url=lead.website,
        redirected_url=_extract_final_url(audit.audit_notes),
        notes="\n".join(audit.top_sales_arguments),
        raw_audit_json={
            "critical_issues": audit.critical_issues,
            "warnings": audit.warnings,
            "opportunities": audit.opportunities,
            "quick_wins": audit.quick_wins,
            "top_sales_arguments": audit.top_sales_arguments,
        },
        raw_pagespeed_json=audit.raw_pagespeed,
        meta_json={"parser_notes": audit.parser_notes},
    )
    db.session.add(detail)

    for severity, entries in [
        ("critical", audit.critical_issues),
        ("warning", audit.warnings),
        ("opportunity", audit.opportunities),
        ("quick_win", audit.quick_wins),
    ]:
        for entry in entries:
            db.session.add(
                AuditIssueModel(
                    audit_result=detail,
                    severity=severity,
                    category=entry["category"],
                    code=entry["category"],
                    title=entry["title"],
                    description=entry["description"],
                    recommendation=entry["recommendation"],
                    score_impact=entry["impact"],
                    is_blocking=severity == "critical",
                    raw_issue_json=entry,
                )
            )
    return detail


def _map_checks(
    checks: list[CheckResult], priorities: list[str], passed: bool
) -> list[dict]:
    return [
        {
            "category": check.category,
            "priority": check.priority,
            "title": check.message,
            "description": check.message,
            "recommendation": check.recommendation,
            "impact": _impact_for_priority(check.priority),
        }
        for check in checks
        if check.priority in priorities and check.passed is passed
    ]


def _impact_for_priority(priority: str) -> float:
    return {"high": 9.0, "medium": 6.0, "low": 3.0}.get(priority, 2.0)


def _build_sales_arguments(
    critical_issues: list[dict], warnings: list[dict], pagespeed: dict, profile
) -> list[str]:
    arguments: list[str] = []
    if critical_issues:
        arguments.append(
            (
                f"{len(critical_issues)} kritische SEO-/Trust-Lücken mit direkter "
                "Sichtbarkeitswirkung identifiziert"
            )
        )
    perf = pagespeed.get("performance_score")
    if isinstance(perf, (int, float)) and perf < 70:
        arguments.append(
            (
                "Performance unter 70: messbares Potenzial für mehr Conversions "
                "und bessere Ads-Qualität"
            )
        )
    if not profile.whatsapp_links:
        arguments.append(
            "Kein WhatsApp-Kanal erkannt: schneller Conversion-Hebel für mobile Leads"
        )
    if warnings:
        arguments.append(
            f"{len(warnings)} mittlere Prioritäten als Quick-Win-Roadmap verfügbar"
        )
    return arguments[:5]


def _checks_with_link_status(crawl) -> list[str]:
    values = list(crawl.checked_pages)
    values.extend(f"{item} -> redirect" for item in crawl.redirects)
    values.extend(f"{item} 404" for item in crawl.broken_links)
    return values


def _extract_final_url(audit_notes: str) -> str | None:
    for line in audit_notes.splitlines():
        if line.startswith("Final URL="):
            return line.replace("Final URL=", "", 1).strip()
    return None


def _score_overall(audit: AuditResult) -> float:
    values = [
        audit.raw_pagespeed.get("performance_score"),
        audit.raw_pagespeed.get("seo_score"),
        100 - (len(audit.critical_issues) * 5),
        100 - (len(audit.warnings) * 2),
    ]
    normalized = [float(v) for v in values if isinstance(v, (int, float))]
    if not normalized:
        return 0.0
    return round(max(0.0, min(100.0, mean(normalized))), 1)
