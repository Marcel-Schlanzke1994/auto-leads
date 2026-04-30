from __future__ import annotations

from app.services.web_perf.heuristics import evaluate_local_heuristics
from app.services.web_perf.models import WebPerfResult
from app.services.web_perf.recommendations import build_recommendations


def analyze_web_perf(fetch_result, pagespeed_data: dict | None) -> WebPerfResult:
    pagespeed_data = pagespeed_data or {}
    heuristics = evaluate_local_heuristics(
        html=getattr(fetch_result, "body", "") or "",
        headers=getattr(fetch_result, "response_headers", {}) or {},
    )

    perf_score = pagespeed_data.get("performance_score")
    result = WebPerfResult(
        performance_score=(
            int(perf_score) if isinstance(perf_score, (int, float)) else None
        ),
        lcp_ms=_as_int(pagespeed_data.get("lcp_ms")),
        cls=_as_float(pagespeed_data.get("cls")),
        inp_ms=_as_int(pagespeed_data.get("inp_ms")),
        tbt_ms=_as_int(pagespeed_data.get("tbt_ms")),
        fcp_ms=_as_int(pagespeed_data.get("fcp_ms")),
        tti_ms=_as_int(pagespeed_data.get("tti_ms")),
        uses_compression=heuristics["uses_compression"],
        cache_policy_present=heuristics["cache_policy_present"],
        render_blocking_risk=heuristics["render_blocking_risk"],
        image_optimization_risk=heuristics["image_optimization_risk"],
        mobile_performance_risk=heuristics["mobile_performance_risk"],
        source=_source_label(pagespeed_data, heuristics),
    )
    result.recommendations = build_recommendations(result)
    return result


def _as_int(value) -> int | None:
    return int(value) if isinstance(value, (int, float)) else None


def _as_float(value) -> float | None:
    return round(float(value), 3) if isinstance(value, (int, float)) else None


def _source_label(pagespeed_data: dict, heuristics: dict) -> str:
    has_ps = any(
        pagespeed_data.get(key) is not None
        for key in ["performance_score", "lcp_ms", "fcp_ms", "inp_ms", "tbt_ms", "cls"]
    )
    has_local = bool(heuristics)
    if has_ps and has_local:
        return "mixed"
    if has_ps:
        return "pagespeed"
    if has_local:
        return "local"
    return "unavailable"
