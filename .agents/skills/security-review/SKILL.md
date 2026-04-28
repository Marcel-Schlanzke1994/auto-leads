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
