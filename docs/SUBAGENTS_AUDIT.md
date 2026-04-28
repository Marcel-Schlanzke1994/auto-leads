# SUBAGENTS Audit

_Stand: 2026-04-28_

## Scope
- Quelle: `https://github.com/VoltAgent/awesome-codex-subagents`
- Geprüfte Dateien: alle `.toml` Agent-Dateien in `.codex/agents/`

## Prüfmethodik
1. statische Suche nach riskanten Sandbox-Modi (`danger-full-access`)
2. statische Suche nach destruktiven Command-Mustern (`rm -rf`, `curl | sh`)
3. Secret-Pattern-Scan (`AKIA`, `ghp_`, private keys, Slack/GitHub token prefixes)
4. Plausibilitätsprüfung auf Rollen-/Instruktionskonflikte

## Ergebnis
- **Keine** Agent-Datei nutzt `danger-full-access`.
- **Keine** hardcodierten Secrets oder Token gefunden.
- **Keine** offensichtlichen destruktiven Shell-Anweisungen in den Instruktionen gefunden.
- Security-/Reviewer-Agenten sind überwiegend `read-only` und damit konform mit Least-Privilege.

## Markierte/entschärfte Agenten
- `agent-installer`: markiert als **operativ sensibel** (kann Installationspfade beeinflussen); Nutzung nur mit explizitem Review.
- `penetration-tester`: markiert als **sicherheitskritisch**; nur in kontrollierten, autorisierten Testumgebungen einsetzen.
- `workflow-orchestrator`/`multi-agent-coordinator`: markiert als **koordinativ kritisch**; Schreibkonflikte durch zentrale Orchestrierung vermeiden.

## Entschärfungen
- Projektweite Leitplanken in `AGENTS.md` ergänzt: security/reviewer bevorzugt read-only, parallele Schreibzugriffe auf dieselben Dateien verboten, ExecPlan-Pflicht für große Features.
- Codex-Defaults in `.codex/config.toml` auf sichere Betriebsmodi gehärtet (workspace-write, on-request, network restricted).

## Restrisiken
- Prompt-Fehlgebrauch durch falsche Delegation bleibt möglich; mit Orchestrator + Reviewer gegensteuern.
- `workspace-write`-Agenten können fehlerhafte Patches erzeugen; CI/Lint/Tests als Guardrail beibehalten.

