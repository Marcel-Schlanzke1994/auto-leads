# lead-scoring

## Purpose
Projekt-Skill zur transparenten Lead-Score-Berechnung.

## When to use
- Wenn Priorisierung für Vertrieb oder Kampagnen benötigt wird.

## Workflow
1. Scoring-Faktoren definieren (Kontaktierbarkeit, SEO, Branchenfit, Aktivität).
2. Gewichte dokumentieren und versionieren.
3. Score + Begründungs-Features persistent speichern.

## Safety Guardrails
- Keine diskriminierenden oder intransparenten Merkmale verwenden.

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
