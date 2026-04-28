# Auto-Lead-System ExecPlan

## 1) Purpose
Ziel ist ein robustes, nachvollziehbares und compliance-fähiges System zur lokalen Lead-Generierung inklusive Suchlauf, Qualitätsanreicherung, Scoring, Review und Export.

## 2) Ist-Analyse
- Flask-App mit App-Factory und Blueprints vorhanden.
- Service-Layer deckt Suche, Audit, SEO, Scoring, Export und Deduplizierung ab.
- SQLAlchemy + Alembic sind etabliert.
- Tests vorhanden, aber Ausbau bei Integrations- und Resilienzfällen sinnvoll.

## 3) Zielarchitektur
- Beibehaltung des modularen Flask-Monolithen.
- Strikte Trennung von Route-Orchestrierung und Fachlogik in Services.
- Optionaler Ausbau zu asynchroner Jobverarbeitung bei Lastanstieg.
- Security- und Observability-Standards als feste Quality Gates.

## 4) Datenmodell
Kernobjekte:
- **Lead**: Firmen-/Kontaktinformationen, Website- und SEO-Merkmale, Scoring, Status
- **SearchJob**: Parameter, Fortschritt, Roh-/Filter-/Ergebniszähler, Fehlerzustand
- **AuditMeta**: technische Prüfergebnisse (Erreichbarkeit, Impressum, Kontaktindikatoren)

Mongo-kompatible Event-Strukturen (bei Event-Streams/Integrationen):
- `google_id`
- `start`
- `event_time`
- `city`
- `keyword`
- `status`
- `payload`

## 5) API
- REST-Endpunkte für Lead-Liste, Lead-Details, Suchstart, Suchprogress.
- JSON-Schemata stabil halten; Breaking Changes versionieren.
- Eingabevalidierung und konsistente Fehlerantworten (`4xx/5xx` + Fehlercode).

## 6) Dashboard
- Fokus auf operative KPIs: Jobs aktiv/fehlgeschlagen, Lead-Qualität, Exporte.
- Drilldown: von Jobübersicht zu Lead-Detail inkl. Score-Begründung.
- UI-Statuswechsel (neu/kontaktiert/qualifiziert etc.) nachvollziehbar protokollieren.

## 7) Extraktion
- Mehrstufig: HTML-Fetch → Inhaltsblöcke → Kontakt-/Impressumserkennung.
- Heuristiken versionieren und mit Regressionstests absichern.
- Timeout- und Retry-Parameter je Quelle konfigurierbar.

## 8) SEO
- Prüfpunkte: Title/Description, Heading-Struktur, Indexierbarkeit, Performance-Signale.
- Ergebnisse als strukturierte Felder für Score/Filter exportieren.

## 9) Google-API
- Primär: Google Places (Text Search + Details), optional PageSpeed.
- Quota-Handling: Intervallsteuerung, Retry mit Backoff, klare Fehlermetrik.
- API-Schlüssel nur aus Umgebung/Secrets.

## 10) DSGVO / Robots / Rate-Limits
- Datensparsamkeit: nur geschäftlich erforderliche Daten speichern.
- Dokumentierte Aufbewahrungs- und Löschregeln.
- robots.txt und Nutzungsbedingungen beachten.
- Service-spezifische Rate-Limits zentral konfigurierbar.

## 11) Security
- CSRF + Rate-Limiter auf Anwendungsebene.
- SSRF-Schutz und URL-Validierung im Fetching.
- Secret-Hygiene in CI/CD und lokaler Entwicklung.
- Security-Incidents mit definiertem Rotationsprozess.

## 12) Tests
Pflicht bei Codeänderungen:
- `pytest`
- `black --check .`
- `flake8`

Zusätzlich empfohlen:
- Integrations-/Smoke-Tests der Suchpipeline
- Contract-Tests für API-Antworten
- Regressionstests für Dedupe/Scoring

## 13) CI/CD
- CI-Workflow für Tests und Linting.
- Codex-Code-Review Workflow für automatisierte PR-Analysen.
- Codex-Auto-Fix Workflow für gezielte Fehlerbehebung mit Secret- und Fork-Schutz.

## 14) Milestones
- **M1**: CI-Härtung, Doku-Basis, stabile Kernpipeline
- **M2**: bessere Extraktion/Scoring-Transparenz, Monitoring
- **M3**: Skalierungsoptionen, Compliance-/Security-Reife

## 15) Decision Log
- D1: Flask-Monolith bleibt bis nach M2 erhalten (geringe operative Komplexität).
- D2: SQLite als Default bleibt für lokalen Betrieb; DB-Abstraktion für spätere Umstellung.
- D3: External Calls bleiben strikt timeout-/rate-limit-gesteuert.

## 16) Surprises
- Höchste Variabilität entsteht durch Webseitenstrukturen, nicht durch API-Schemas.
- Datenqualität variiert regional stark; Dedupe muss mehrdimensional bleiben.

## 17) Outcomes
- Reproduzierbare Lead-Ergebnisse mit auditierbarer Herleitung.
- Schnellere Fehlersuche durch klaren Datenfluss und bessere Betriebsdokumentation.
- Höhere Betriebssicherheit durch verbindliche CI-/Security-Gates.

## 18) Subagent Integration Update (2026-04-28)
### Why
- Vollständige Integration eines kuratierten Subagent-Katalogs, damit Codex Aufgaben rollenbasiert, sicher und nachvollziehbar delegieren kann.
- Ziel: bessere Planbarkeit, höhere Review-Qualität und geringere Fehlerrisiken bei komplexen Änderungen.

### Chosen structure
- Alle Agent-Dateien liegen projektlokal in `.codex/agents/`.
- Basis: 136 Agents aus `awesome-codex-subagents`.
- Ergänzung: 8 projektbezogene Alias-Agenten (`planner`, `orchestrator`, `database-architect`, `test-engineer`, `ci-cd-specialist`, `documentation-writer`, `performance-optimizer`, `scraper-extractor`).
- Kuration und Nutzungsleitfaden in `docs/SUBAGENTS.md`.
- Sicherheitsprüfung und Markierungen in `docs/SUBAGENTS_AUDIT.md`.

### Security decisions
- Keine Übernahme von `danger-full-access`-Konfigurationen.
- Sicherheits-/Reviewer-Rollen bevorzugt read-only.
- Schreibkonflikte werden organisatorisch unterbunden (keine parallelen Writes auf dieselben Dateien).
- Codex-Workspace-Defaults gehärtet: `workspace-write`, `on-request`, `network = restricted`.

### Future usage in Codex
- Komplexe Features starten mit `planner` + ExecPlan-Update.
- Multi-Teilaufgaben über `orchestrator` mit klaren Integrations-Gates.
- Security/Review/Test/CI explizit über spezialisierte Agenten routen.

### Validation checklist
- Dateistruktur geprüft (`.codex/agents/`, `docs/`).
- TOML syntaktisch validierbar (per Python `tomllib`).
- Secret-Pattern-Scan ohne Treffer.
- Risiko-Scan auf destruktive Agent-Prompts ohne kritische Findings.

### Progress
- Status: done
- Last update: 2026-04-28
- Completed since last update:
  - 136 externe Subagents integriert.
  - 8 projektbezogene Alias-Subagents ergänzt.
  - AGENTS-, Config-, Audit- und Katalogdokumentation aktualisiert.
- Next actions:
  - Team-Onboarding für empfohlene Kern-Agenten.
  - Optional: rollenbasierte Prompt-Templates ergänzen.
- Open blockers:
  - keine

### Decision Log Addendum
- Date: 2026-04-28
  - Decision: Vollständige Übernahme des Community-Katalogs plus projektspezifische Alias-Agenten.
  - Rationale: Maximale Abdeckung bei gleichzeitiger klarer Projektsteuerung.
  - Alternatives considered: Nur Teilmenge importieren.
  - Impact: Höherer Agent-Footprint, aber bessere Delegationsfähigkeit.
- Date: 2026-04-28
  - Decision: Sicherheitsrelevante Agenten primär read-only, globale Defaults gehärtet.
  - Rationale: Least-Privilege und geringeres Fehlerrisiko.
  - Alternatives considered: Schnellere, aber permissivere Defaults.
  - Impact: Sichere Standardausführung, bewusste Eskalation nur bei Bedarf.

### Outcomes Addendum
- Subagent-Ökosystem ist vollständig im Projekt verankert.
- Delegation wird reproduzierbar, auditierbar und rollenbasiert.
- Security- und Review-Prozesse sind operationalisiert.

