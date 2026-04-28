# security-review

## Purpose
Threat-orientierte Sicherheitsprüfung für Lead- und Scraping-Workflows.

## When to use
- Bei Änderungen an API-Routen, externen Requests, Exporten, Auth/CSRF/Rate-Limits.

## Workflow
1. Eingaben validieren und SSRF-/Injection-Risiken prüfen.
2. Secrets-Handling: nur Umgebungsvariablen, keine Hardcodes.
3. Crawler/Extraction auf robots.txt, ToS, DSGVO und Fair-Use prüfen.
4. Netzwerkaufrufe auf Timeouts, Retries, Backoff und Domain-Allowlist prüfen.

## Safety Guardrails
- Keine Anleitung für missbräuchliche Nutzung geben.
- Bei kritischen Funden Stop-the-line und Remediation-Plan dokumentieren.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.

## Finding Schema (verbindlich für Findings)
Jedes Finding MUSS folgende Felder enthalten:
- `severity` (`critical|high|medium|low`)
- `confidence` (`high|medium|low`)
- `impact`
- `prerequisites`
- `mitigation`
- `residual risk`
- `affected files`
- `evidence`

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
