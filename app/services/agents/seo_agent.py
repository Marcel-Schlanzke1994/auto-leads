from __future__ import annotations

from app.services.agents.base import AgentContext, AgentResult, BaseAgent
from app.services.website_fetcher import fetch_website
from app.services.seo_check_service import analyze_seo


class SEOAgent(BaseAgent):
    name = "seo"

    def run(self, context: AgentContext) -> AgentResult:
        if not context.website:
            return AgentResult(
                agent_name=self.name, status="skipped", errors=["missing_website"]
            )

        fetch = fetch_website(context.website, timeout=10.0)
        signals = analyze_seo(fetch.body)
        payload = {
            "site_title": signals.site_title,
            "meta_description": signals.meta_description,
            "has_h1": signals.has_h1,
            "has_cta": signals.has_cta,
            "mobile_signals": signals.mobile_signals,
            "final_url": fetch.url,
        }
        context.state["seo"] = payload
        return AgentResult(agent_name=self.name, status="ok", payload=payload)
