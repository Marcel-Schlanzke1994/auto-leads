# database-design

## Purpose
Datenmodell-Design mit Migrations- und Compliance-Fokus.

## When to use
- Bei Schemaänderungen, neuen Entities, Dedupe-/Scoring-Feldern.

## Workflow
1. Entity-Grenzen und Beziehungen definieren.
2. Normalisierung vs. Query-Performance abwägen.
3. Migration (Alembic), Rollback und Backfill planen.
4. Aufbewahrung und Löschkonzept für personenbezogene Daten prüfen.

## Safety Guardrails
- Keine direkten Modelländerungen ohne Migration.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
