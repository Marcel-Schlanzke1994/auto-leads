# impressum-extraction

## Purpose
Projekt-Skill zur Impressum-/Kontakt-Extraktion aus DACH-Webseiten.

## When to use
- Wenn rechtlich relevante Kontaktangaben fehlen.

## Workflow
1. Kandidatenseiten erkennen (`/impressum`, `/kontakt`, Footer-Links).
2. E-Mail, Telefon, Firma, Adresse mit heuristischen Mustern extrahieren.
3. Treffer mit Confidence-Score + Quell-URL speichern.

## Safety Guardrails
- Nur öffentlich zugängliche Daten; DSGVO-konforme Speicherung.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
