# web-extraction

## Purpose
Extrahiert Kontakt- und Firmeninformationen aus Webseiten.

## When to use
- Bei Bedarf an Impressum/Kontakt-Anreicherung.

## Workflow
1. Zielseiten priorisieren (Startseite, Kontakt, Impressum).
2. Regex + DOM-Heuristiken kombinieren, Ergebnisse confidence-basiert kennzeichnen.
3. Extraktionsergebnisse gegen bekannte Muster normalisieren.

## Safety Guardrails
- Keine Login-Bereiche umgehen; keine Bot-Evasion-Techniken verwenden.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
