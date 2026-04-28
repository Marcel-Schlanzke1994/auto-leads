# test-generation

## Purpose
Erzeugt zielgerichtete Tests für Services, Routen und Datenregeln.

## When to use
- Bei neuem Verhalten, Bugfixes, Scoring-/Dedupe-Regeln.

## Workflow
1. Given/When/Then-Fälle aus Anforderungen ableiten.
2. Happy path + edge cases + Fehlerpfade abdecken.
3. Mocks nur an externen API-Grenzen einsetzen.
4. Testnamen domänennah formulieren (Lead, Job, Audit, Export).

## Safety Guardrails
- Keine flakigen Netzwerkabhängigkeiten in Unit-Tests.
- Keine Testdaten mit echten personenbezogenen Daten.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
