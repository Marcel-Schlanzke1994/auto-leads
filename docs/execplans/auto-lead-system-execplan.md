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
