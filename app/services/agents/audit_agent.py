from __future__ import annotations

from app.services.agents.base import AgentContext, AgentResult, BaseAgent
from app.services.website_audit_service import audit_website


class AuditAgent(BaseAgent):
    name = "audit"

    def run(self, context: AgentContext) -> AgentResult:
        if not context.website:
            return AgentResult(
                agent_name=self.name, status="skipped", errors=["missing_website"]
            )

        audit = audit_website(context.website, timeout=10.0)
        payload = {
            "critical_issues": audit.critical_issues,
            "warnings": audit.warnings,
            "quick_wins": audit.quick_wins,
            "top_sales_arguments": audit.top_sales_arguments,
            "raw_pagespeed": audit.raw_pagespeed,
        }
        context.state["audit"] = payload
        return AgentResult(agent_name=self.name, status="ok", payload=payload)
