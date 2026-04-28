from __future__ import annotations

from app.models import Lead
from app.services.agents.base import AgentContext, AgentResult, BaseAgent
from app.services.outreach_draft_service import generate_outreach_draft


class OutreachAgent(BaseAgent):
    name = "outreach"

    def run(self, context: AgentContext) -> AgentResult:
        compliance = context.state.get("compliance") or {}
        if compliance.get("blocked"):
            return AgentResult(
                agent_name=self.name, status="blocked", payload={"draft_created": False}
            )

        lead = Lead.query.get(context.lead_id)
        if not lead:
            return AgentResult(
                agent_name=self.name, status="error", errors=["lead_not_found"]
            )

        draft = generate_outreach_draft(lead=lead, channel=context.channel)
        payload = {
            "draft_created": draft.status == "ok" and bool(draft.body),
            "draft_only": True,
            "subject": draft.subject,
            "body": draft.body,
            "status": draft.status,
            "error_code": draft.error_code,
            "error_message": draft.error_message,
        }
        context.state["outreach"] = payload
        return AgentResult(
            agent_name=self.name,
            status="ok" if draft.status == "ok" else draft.status,
            payload=payload,
        )
