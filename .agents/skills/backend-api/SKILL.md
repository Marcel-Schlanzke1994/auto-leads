# backend-api

## Purpose
Implementiert robuste Flask-Backend-APIs im bestehenden App-Factory-Muster.

## When to use
- Bei neuen Endpunkten oder Service-Orchestrierung.

## Workflow
1. Blueprint erweitern statt ad-hoc Routen.
2. Business-Logik in `app/services/` kapseln.
3. Input validieren, konsistente Fehlerstruktur liefern, Rate-Limits respektieren.
4. Tests für Security, Validation und Erfolgspfade ergänzen.

## Safety Guardrails
- Keine Umgehung von CSRF-/Rate-Limits.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
