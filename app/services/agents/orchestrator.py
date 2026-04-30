from __future__ import annotations

from dataclasses import dataclass

from app.services.agents.audit_agent import AuditAgent
from app.services.agents.base import AgentContext, AgentResult
from app.services.agents.compliance_agent import ComplianceAgent
from app.services.agents.outreach_agent import OutreachAgent
from app.services.agents.seo_agent import SEOAgent


@dataclass(slots=True)
class OrchestrationResult:
    status: str
    steps: list[AgentResult]


class LeadOrchestrator:
    def __init__(self) -> None:
        self.seo_agent = SEOAgent()
        self.audit_agent = AuditAgent()
        self.compliance_agent = ComplianceAgent()
        self.outreach_agent = OutreachAgent()

    def run(self, context: AgentContext) -> OrchestrationResult:
        steps: list[AgentResult] = []
        for agent in (
            self.seo_agent,
            self.audit_agent,
            self.compliance_agent,
            self.outreach_agent,
        ):
            result = agent.run(context)
            steps.append(result)
            if result.status == "error":
                return OrchestrationResult(status="error", steps=steps)
        return OrchestrationResult(status="ok", steps=steps)
