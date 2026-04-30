# Skills-Katalog für auto-leads

_Stand: 2026-04-28_

Dieses Projekt nutzt Skills aus dem kuratierten Katalog unter `.agents/skills/`.
Skills werden **nur aufgabenbezogen** geladen. Für Security-, Review-, Testing- und CI/CD-relevante Änderungen gelten verpflichtende Evidence- und Gate-Regeln.

## Nutzungsprinzipien (verbindlich)

1. Skills **kontextarm und selektiv** laden (kein Bulk-Loading).
2. Bei passenden Aufgaben Security-/Review-/Testing-/CI-Skills priorisieren.
3. Bei großen Änderungen zuerst ExecPlan gemäß `.agent/PLANS.md` erstellen/aktualisieren.
4. Für Security/API/Crawling/DB/CI-Änderungen ist das Multi-Agent-Gate (`docs/MULTI_AGENT_GATE.md`) verpflichtend.
5. Für Codeänderungen gelten die Projekt-Quality-Gates (`pytest`, `black --check .`, `flake8`) mit dokumentierter Evidence.

## Skill-Auswahlmatrix (Task-Klassen)

| Task-Klasse | Empfohlene Skills | Empfohlene Subagents | Pflichtnachweise |
|---|---|---|---|
| Bugfix | `debug`, `test-generation`, `code-review`, `commit` | `planner`, `backend-developer`, `reviewer`, `test-engineer` | Repro-Schritte, Fix-Evidence, Test/Lint-Output, Residual-Risiko |
| API-Änderung | `backend-api`, `api-documentation`, `security-review`, `code-review`, `test-generation` | `planner`, `api-designer`, `reviewer`, `security-auditor`, `test-engineer` | Request/Response-Vertrag, Security-Findings, Runtime-Verifikation externer APIs, Test/Lint |
| Datenmodelländerung | `database-design`, `backend-api`, `test-generation`, `code-review` | `planner`, `database-architect`, `reviewer`, `security-auditor` | Migrationsplan inkl. Rollback, Datenrisiken, betroffene Queries/Services, Test/Lint |
| Crawling/Web-Extraction | `web-extraction`, `website-audit`, `security-review`, `test-generation`, `code-review` | `planner`, `scraper-extractor`, `security-auditor`, `reviewer` | robots/ToS-Check, Rate-Limit-Definition, PII-Minimierung, Runtime-Verifikation, Test/Lint |
| SEO-Audit | `local-seo-audit`, `website-audit`, `report-generation`, `code-review` | `planner`, `seo-specialist`, `reviewer` | Auditkriterien, evidenzbasierte Findings, Priorisierung, Residual-Risiko |
| Lead-Export | `lead-export`, `export-csv-excel`, `security-review`, `code-review`, `test-generation` | `planner`, `data-engineer`, `security-auditor`, `reviewer` | Feld-Whitelist, PII-Check, Export-Metadaten, Test/Lint |
| Dashboard/UI | `frontend-ui`, `dashboard-design`, `test-generation`, `code-review` | `planner`, `frontend-developer`, `reviewer`, `test-engineer` | UI-Zustandsabdeckung (loading/error/empty), Accessibility-Hinweise, Test/Lint |
| CI/CD | `ci-failure-resolution`, `documentation`, `security-review`, `code-review` | `planner`, `ci-cd-specialist`, `devops-engineer`, `security-auditor`, `reviewer` | Pipeline-Diff, Rollback-Strategie, Security-Checks, Nachweis grüner Checks |
| Security-Fix | `security-review`, `code-review`, `test-generation`, `documentation`, `commit` | `planner`, `security-auditor`, `reviewer`, `test-engineer` | Finding-Schema vollständig, Mitigation + Residual-Risk, Test/Lint, Gate-Entscheidung |
| Dokumentation | `documentation`, `api-documentation`, `report-generation` (bei Bedarf) | `planner`, `documentation-writer`, `reviewer` | Aktualisierte Artefakte, Scope/Impact, begründete Doku-only-Ausnahme für Tests |

## Pflicht-Evidence je Task

Unabhängig vom Skill müssen Ergebnisberichte mindestens enthalten:

- Scope und getroffene Annahmen.
- Ausgeführte Kommandos inkl. Exit-Status.
- Betroffene Dateien/Artefakte.
- Offene Risiken, Mitigation und Residual Risk.
- Bei externen Integrationen: Runtime-Verifikationsstatus.

## Referenzen

- Skill-Findings und Umsetzung: `docs/SKILLS_REVIEW.md`
- Multi-Agent-Gate: `docs/MULTI_AGENT_GATE.md`
- Security-Evidence-Standard: `docs/SECURITY_EVIDENCE.md`
- Planpflicht und Trigger: `.agent/PLANS.md`
