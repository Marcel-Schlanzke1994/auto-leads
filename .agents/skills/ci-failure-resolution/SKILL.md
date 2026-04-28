# ci-failure-resolution

## Purpose
Schnelle und sichere Behebung von CI-Fehlern.

## When to use
- Wenn GitHub Actions fehlschlagen oder Lint/Test regressieren.

## Workflow
1. Fehlerlog lesen, ersten kausalen Fehler isolieren.
2. Lokal mit identischem Befehl reproduzieren.
3. Fix kleinstmöglich halten und erneuten CI-Lauf verifizieren.
4. Wenn Umgebung abweicht: Ursache dokumentieren und Workaround begrenzen.

## Safety Guardrails
- Keine Umgehung durch Abschalten von Jobs ohne Change-Management.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
