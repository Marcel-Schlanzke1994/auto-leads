# code-review

## Purpose
Strukturiertes Review für Python/Flask, API- und Datenflussqualität.

## When to use
- Vor Merge jeder produktiven Änderung.
- Bei Refactorings oder Schnittstellenänderungen.

## Workflow
1. Änderung gegen Anforderungen und ExecPlan spiegeln.
2. Prüfen: Lesbarkeit, Fehlerpfade, Abwärtskompatibilität, Tests.
3. Spezifisch für auto-leads: Service-Layer in `app/services/` beibehalten.
4. Review-Output: Findings nach Severity (high/medium/low).

## Safety Guardrails
- Keine pauschalen Approvals ohne reproduzierbare Begründung.
- Security- und Datenschutzaspekte immer separat ausweisen.

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
