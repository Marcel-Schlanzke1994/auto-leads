from app.extensions import db
from app.models import Lead, OptOut
from app.services.agents.base import AgentContext, AgentResult
from app.services.agents.orchestrator import LeadOrchestrator


def _lead(**overrides):
    base = {
        "company_name": "Agent Test GmbH",
        "source_query": "seo berlin",
        "website": "https://agent.example",
        "email": "team@agent.example",
        "email_normalized": "team@agent.example",
        "status": "new",
    }
    base.update(overrides)
    return Lead(**base)


def test_orchestrator_executes_compliance_before_outreach(app):
    order = []
    orchestrator = LeadOrchestrator()

    class _Stub:
        def __init__(self, name):
            self.name = name

        def run(self, context):
            del context
            order.append(self.name)
            return AgentResult(agent_name=self.name, status="ok")

    orchestrator.seo_agent = _Stub("seo")
    orchestrator.audit_agent = _Stub("audit")
    orchestrator.compliance_agent = _Stub("compliance")
    orchestrator.outreach_agent = _Stub("outreach")

    with app.app_context():
        result = orchestrator.run(
            AgentContext(lead_id=1, website="https://agent.example")
        )

    assert result.status == "ok"
    assert order.index("compliance") < order.index("outreach")


def test_outreach_is_blocked_when_compliance_blocks(app):
    with app.app_context():
        lead = _lead()
        db.session.add(lead)
        db.session.flush()
        db.session.add(
            OptOut(
                channel="email",
                email=lead.email,
                email_normalized=lead.email_normalized,
            )
        )
        db.session.commit()

        orchestrator = LeadOrchestrator()

        class _Noop:
            def __init__(self, name):
                self.name = name

            def run(self, context):
                del context
                return AgentResult(agent_name=self.name, status="ok")

        orchestrator.seo_agent = _Noop("seo")
        orchestrator.audit_agent = _Noop("audit")

        result = orchestrator.run(
            AgentContext(lead_id=lead.id, website=lead.website, channel="email")
        )

    compliance_step = next(
        step for step in result.steps if step.agent_name == "compliance"
    )
    outreach_step = next(step for step in result.steps if step.agent_name == "outreach")

    assert compliance_step.payload["blocked"] is True
    assert outreach_step.status == "blocked"
    assert outreach_step.payload["draft_created"] is False
