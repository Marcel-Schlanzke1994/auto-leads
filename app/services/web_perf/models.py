from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal

RiskLevel = Literal["low", "medium", "high", "unknown"]
SourceType = Literal["pagespeed", "local", "mixed", "unavailable"]


@dataclass(slots=True)
class WebPerfResult:
    performance_score: int | None = None
    lcp_ms: int | None = None
    cls: float | None = None
    inp_ms: int | None = None
    tbt_ms: int | None = None
    fcp_ms: int | None = None
    tti_ms: int | None = None
    uses_compression: bool | None = None
    cache_policy_present: bool | None = None
    render_blocking_risk: RiskLevel = "unknown"
    image_optimization_risk: RiskLevel = "unknown"
    mobile_performance_risk: RiskLevel = "unknown"
    recommendations: list[str] = field(default_factory=list)
    source: SourceType = "unavailable"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
