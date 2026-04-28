# debug

## Purpose
Systematische Fehleranalyse mit reproduzierbaren Schritten.

## When to use
- Bei fehlschlagenden Tests, CI-Fehlern, inkonsistenten Leads.

## Workflow
1. Fehlerbild mit exakten Kommandos reproduzieren.
2. Hypothesen priorisieren (Config, Daten, Code, externe API).
3. Minimalen Fix implementieren und Nebeneffekte durch Regressionstests prüfen.
4. Root-Cause + Preventive Action im Ergebnisbericht festhalten.

## Safety Guardrails
- Keine blindes Trial-and-Error in produktiven Konfigurationen.
- Keine Deaktivierung von Sicherheits-/Validierungschecks als Dauerlösung.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.

## Definition of Done
- Der Scope aus `When to use` und `Workflow` ist vollständig bearbeitet und im Ergebnisbericht nachvollziehbar.
- Alle getroffenen Annahmen, Risiken und Folgeaufgaben sind explizit dokumentiert.
- Änderungen an produktivem Code sind mit projektweiten Checks (`pytest`, `black --check .`, `flake8`) validiert oder als Doku-only begründet.

## Required Evidence
- Auflistung der ausgeführten Befehle inkl. Exit-Status.
- Referenz auf geänderte Dateien/Artefakte (Pfad + Zweck).
- Bei externen Abhängigkeiten: dokumentiert, was lokal verifiziert wurde und was Runtime-/Produktiv-Verifikation benötigt.

## Out-of-scope
- Keine Änderung von Anforderungen außerhalb des vereinbarten Task-Scopes.
- Keine Umgehung bestehender Security-, Compliance- oder Governance-Regeln.
- Keine stillen Breaking Changes ohne explizite Dokumentation und Migrationshinweis.

## Quality Gates
- Scope vollständig, nachvollziehbar und gegen Anforderungen gespiegelt.
- Security/Privacy-Guardrails wurden explizit geprüft und dokumentiert.
- Ergebnis enthält klare Merge-Empfehlung oder offene Blocker mit nächstem Schritt.
