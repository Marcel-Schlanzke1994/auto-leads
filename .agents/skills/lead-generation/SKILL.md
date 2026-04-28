# lead-generation

## Purpose
Steuert lokale Lead-Discovery von Suchanfrage bis qualifizierter Liste.

## When to use
- Bei neuen Suchjobs und Standort-/Keyword-Kampagnen.

## Workflow
1. Suchparameter (city, keyword, radius) definieren.
2. Quellen abrufen (z. B. Google Places) mit Quota- und Retry-Kontrolle.
3. Rohdaten validieren, deduplizieren und mit Audit-Features anreichern.

## Safety Guardrails
- Nur geschäftlich notwendige Daten speichern; DSGVO beachten.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
