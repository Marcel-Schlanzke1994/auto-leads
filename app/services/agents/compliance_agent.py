from __future__ import annotations

from app.models import Lead
from app.services.agents.base import AgentContext, AgentResult, BaseAgent
from app.services.outreach_draft_service import check_outreach_block


class ComplianceAgent(BaseAgent):
    name = "compliance"

    def run(self, context: AgentContext) -> AgentResult:
        lead = Lead.query.get(context.lead_id)
        if not lead:
            return AgentResult(
                agent_name=self.name, status="error", errors=["lead_not_found"]
            )

        block = check_outreach_block(lead=lead, channel=context.channel)
        payload = {
            "blocked": block.blocked,
            "status": block.status,
            "reason": block.reason,
            "matched_field": block.matched_field,
            "matched_value": block.matched_value,
        }
        context.state["compliance"] = payload
        return AgentResult(agent_name=self.name, status="ok", payload=payload)
