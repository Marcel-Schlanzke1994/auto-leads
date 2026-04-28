# commit

## Purpose
Sichere Git-Commits mit klarer Historie.

## When to use
- Wenn eine Änderung vollständig validiert wurde.
- Vor PR-Erstellung mit konsistentem Commit-Message-Schema.

## Workflow
1. Arbeitsbaum mit `git status --short` prüfen.
2. Diff thematisch clustern und nur relevante Dateien committen.
3. Commit-Message: `<type>(scope): summary` + Sicherheits-/Risiko-Hinweis im Body.
4. Vor Commit sicherstellen: keine Secrets, keine temporären Artefakte.

## Safety Guardrails
- Keine destruktiven Git-Befehle (`reset --hard`, `clean -fd`, force push) ohne explizite Notwendigkeit.
- Kein Commit von `.env`, Tokens oder personenbezogenen Rohdaten.

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
