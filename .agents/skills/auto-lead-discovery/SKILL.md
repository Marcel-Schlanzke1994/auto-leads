# auto-lead-discovery

## Purpose
Projekt-Skill für sichere lokale Lead-Discovery mit Google Places API.

## When to use
- Wenn neue lokale Lead-Kampagnen geplant werden.

## Workflow
1. Keyword + Standort + Suchradius definieren und dokumentieren.
2. Google Places Text Search/Details mit API-Key aus `os.getenv` ausführen.
3. Ratenbegrenzung, Backoff und Fehlerquoten überwachen.
4. Ergebnisse in Lead-Objekte transformieren und deduplizieren.

## Safety Guardrails
- Keine hardcodierten API-Keys; ToS/Quota strikt einhalten.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
