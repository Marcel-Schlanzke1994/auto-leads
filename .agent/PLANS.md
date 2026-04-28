# Projektweite Planungsregeln

## Ziel
`.agent/PLANS.md` dient als zentrale Referenz für Meilensteinplanung, Priorisierung und Nachverfolgung in Auto-Leads.

## Planungsregeln
1. **Outcome vor Output**: jedes Vorhaben beschreibt messbaren Nutzen (z. B. bessere Lead-Qualität, geringere Laufzeit).
2. **Kleine Inkremente**: Features in vertikale Scheiben (API, Service, UI, Tests, Doku) aufteilen.
3. **Explizite Risiken**: pro Meilenstein mindestens ein technisches und ein operatives Risiko benennen.
4. **Definition of Done**:
   - Implementierung abgeschlossen
   - Tests/Lint grün oder dokumentierte Ausnahme
   - Doku aktualisiert
   - Migrations-/Rollback-Pfad klar
5. **Security Gate**: Änderungen mit externer API, Crawling oder Datenexport benötigen Security-/Compliance-Review.

## Milestone-Tracking (Template)

## M1 – Stabiler Kernbetrieb
- Status: geplante Arbeiten
- Scope: Suchjob-Stabilität, Dublettenqualität, Dashboard-Basiskennzahlen
- KPIs: Fehlerquote Jobs < 2 %, mindestens 95 % erfolgreiche Exporte
- Risiken: API-Quota, inkonsistente Input-Daten

## M2 – Qualitätssteigerung Leads
- Status: geplant
- Scope: Scoring-Transparenz, Audit-Tiefe, bessere Domain-/Kontakt-Extraktion
- KPIs: +15 % verwertbare Leads gegenüber M1-Baseline
- Risiken: Heuristik-Fehlklassifikation, längere Laufzeiten

## M3 – Operativer Reifegrad
- Status: geplant
- Scope: Monitoring/Alerting, Recovery-Playbooks, CI/CD-Härtung
- KPIs: Mean Time to Recovery < 30 min, CI-Erfolgsquote > 95 %
- Risiken: Tooling-Komplexität, Wartungsaufwand
