from __future__ import annotations

from app.services.web_perf.models import WebPerfResult


def build_recommendations(result: WebPerfResult) -> list[str]:
    recs: list[str] = []
    if result.lcp_ms and result.lcp_ms > 2500:
        recs.append(
            "LCP-Bild priorisieren und kritische Above-the-fold-Assets vorladen."
        )
    if result.image_optimization_risk == "high":
        recs.append(
            "Große Bilder komprimieren und moderne Formate wie WebP/AVIF prüfen."
        )
    if result.render_blocking_risk in {"medium", "high"}:
        recs.append(
            "Nicht kritisches JavaScript verzögert laden (defer/async) "
            "und CSS reduzieren."
        )
    if result.cache_policy_present is False:
        recs.append(
            "Browser-Caching mit Cache-Control, ETag oder Last-Modified verbessern."
        )
    if result.uses_compression is False:
        recs.append("HTTP-Kompression (gzip oder br) serverseitig aktivieren.")
    if result.mobile_performance_risk in {"medium", "high"}:
        recs.append(
            "Mobile Darstellung prüfen und viewport-/layout-kritische "
            "Ressourcen optimieren."
        )
    if result.source in {"local", "unavailable"}:
        recs.append(
            "Core Web Vitals ergänzend mit der optionalen PageSpeed API verifizieren."
        )
    return recs[:6]
