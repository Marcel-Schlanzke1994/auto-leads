# Agents Architecture (Step 1)

Dieses Dokument beschreibt die erste Integrationsstufe für `app/services/agents/`.

## Ziele von Schritt 1

- Agent-Schicht als dünne Orchestrierung über bestehenden Services.
- Kein Rewrite: vorhandene Audit-/SEO-/Outreach-Funktionalität bleibt Quelle der Wahrheit.
- Compliance-Gate vor Outreach.
- Outreach erzeugt ausschließlich Drafts (kein Versand, kein Bulk-Send).

## Komponenten

- `base.py`
  - `AgentContext`: gemeinsame Laufzeitdaten (Lead, Website, Kanal, State).
  - `AgentResult`: standardisiertes Ergebnis je Agent.
  - `BaseAgent`: Interface.

- `seo_agent.py`
  - Nutzt `fetch_website` + `analyze_seo`.
  - Schreibt SEO-Signale in `context.state["seo"]`.

- `audit_agent.py`
  - Nutzt `audit_website`.
  - Schreibt priorisierte Findings in `context.state["audit"]`.

- `compliance_agent.py`
  - Nutzt `check_outreach_block`.
  - Schreibt Block-Status in `context.state["compliance"]`.

- `outreach_agent.py`
  - Prüft zuerst Compliance-Status aus Context.
  - Nutzt `generate_outreach_draft`.
  - Erzeugt Draft-Payload (subject/body) ohne Versand.

- `orchestrator.py`
  - `LeadOrchestrator` führt Agenten in fester Reihenfolge aus:
    1. SEO
    2. Audit
    3. Compliance
    4. Outreach

## Sicherheits- und Compliance-Verhalten

- Kein Versandpfad implementiert.
- Kein Massenversand (nur einzelner `lead_id` pro Run).
- Bei Compliance-Block wird Outreach als `blocked` beendet.

## Betriebsverhalten

- App-Factory/Blueprint-Architektur bleibt unverändert.
- Integration ist additive und beeinflusst App-Start nicht.
