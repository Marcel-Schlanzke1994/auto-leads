# Skills-Katalog für auto-leads

Dieses Projekt nutzt Skills aus dem Awesome-Agent-Skills-Ökosystem **kuratiert und sicherheitsgeprüft**. Skills liegen lokal unter `.agents/skills/` und werden **nur bei Aufgaben-Fit** geladen.

## Priorisierte Kernskills

| Skill | Kurzbeschreibung | Empfohlene Nutzung | Auto-Lead-Relevanz | Sicherheitslevel | Beispielprompt |
|---|---|---|---|---|---|
| `commit` | Sichere, nachvollziehbare Commits | Vor jedem PR | Hoch | Hoch | "Nutze `commit` und erstelle einen sauberen Commit für die aktuellen Änderungen." |
| `code-review` | Qualitäts- und Architekturreview | Vor Merge | Hoch | Hoch | "Führe mit `code-review` ein Severity-basiertes Review durch." |
| `security-review` | Threat-orientierte Sicherheitsprüfung | API/Crawler/Export-Änderungen | Sehr hoch | Kritisch | "Nutze `security-review` für die neuen Web-Extraction-Flows." |
| `debug` | Reproduzierbare Fehleranalyse | Bei Test-/CI-Fehlern | Hoch | Mittel | "Nutze `debug`, reproduziere und behebe den flake8-Fehler." |
| `test-generation` | Testfälle für Services und Routen | Bei neuer Logik | Sehr hoch | Hoch | "Nutze `test-generation` für den neuen Lead-Scoring-Pfad." |
| `ci-failure-resolution` | CI-Fehler beheben | Bei GH-Action-Fehlern | Hoch | Hoch | "Nutze `ci-failure-resolution` für den failing ci.yml Lauf." |
| `documentation` | Tech-Doku und Runbooks | Architektur-/Prozessänderungen | Hoch | Hoch | "Nutze `documentation`, aktualisiere ARCHITECTURE und OPERATIONS." |
| `api-documentation` | API-Verträge und Fehlercodes | API-Änderungen | Hoch | Hoch | "Nutze `api-documentation` für neue `/api/leads` Felder." |
| `database-design` | Modell-/Migrationsdesign | Schemaänderungen | Hoch | Hoch | "Nutze `database-design` für neue AuditMeta-Felder." |
| `backend-api` | Flask-App-Factory-konforme API-Umsetzung | Backend-Features | Sehr hoch | Hoch | "Nutze `backend-api` für einen neuen SearchJob-Endpunkt." |
| `frontend-ui` | UI-Verbesserungen in Templates/JS | Dashboard/Lead-Ansichten | Mittel | Mittel | "Nutze `frontend-ui` für bessere Empty/Error-States." |
| `local-seo-audit` | Lokale SEO-Basisanalyse | Audit- und Priorisierung | Sehr hoch | Hoch | "Nutze `local-seo-audit` für Leads aus München." |
| `website-audit` | Technische Websitechecks | Qualitätsanreicherung | Sehr hoch | Hoch | "Nutze `website-audit` für neue Lead-URLs." |
| `lead-generation` | End-to-End Lead Discovery | Suchkampagnen | Sehr hoch | Hoch | "Nutze `lead-generation` für Keyword `zahnarzt` in Köln." |
| `web-extraction` | Kontakt-/Firmendaten aus Webseiten | Datenergänzung | Sehr hoch | Kritisch | "Nutze `web-extraction` und extrahiere Kontaktpunkte DSGVO-konform." |
| `report-generation` | Management- und Ops-Reports | Regelberichte | Hoch | Hoch | "Nutze `report-generation` und erstelle den Wochenreport." |
| `data-cleaning` | Normalisierung + Dedupe-Vorbereitung | Importe/Qualitätsverbesserung | Hoch | Hoch | "Nutze `data-cleaning` für uneinheitliche Telefonnummern." |
| `export-csv-excel` | Sicherer CSV/XLSX Export | CRM-Übergabe | Hoch | Hoch | "Nutze `export-csv-excel` für qualifizierte Leads." |
| `dashboard-design` | KPI-Visualisierung | Dashboard-Weiterentwicklung | Mittel | Mittel | "Nutze `dashboard-design` für Score-Verteilung + Drilldown." |

## Auto-Lead-spezifische Skills

| Skill | Schwerpunkt |
|---|---|
| `auto-lead-discovery` | Google Places API, Quota-Handling, Dedupe |
| `impressum-extraction` | Impressum/Kontakt-Erkennung für DACH-Websites |
| `local-seo-audit` | NAP-Konsistenz, SEO-Basisprüfungen |
| `lead-scoring` | Transparente Scoring-Regeln und Gewichtung |
| `lead-export` | Deduplizierter Export mit Feld-Whitelist |
| `client-report-generation` | Kundentaugliche Reports mit Risiken + Maßnahmen |

## Nutzungsprinzipien

1. Skills **kontextarm und selektiv** laden (kein Bulk-Loading).
2. Security-/Review-/Testing-/CI-Skills bei passenden Aufgaben zuerst nutzen.
3. Bei großen Features zuerst ExecPlan in `docs/execplans/` anlegen/aktualisieren.
4. Scraping-/Lead-Workflows nur mit DSGVO-, robots.txt-, ToS- und Rate-Limit-Konformität.
