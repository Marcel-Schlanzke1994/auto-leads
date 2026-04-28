# debug

## Purpose
Systematische Fehleranalyse mit reproduzierbaren Schritten.

## When to use
- Bei fehlschlagenden Tests, CI-Fehlern, inkonsistenten Leads.

## Workflow
1. Fehlerbild mit exakten Kommandos reproduzieren.
2. Hypothesen priorisieren (Config, Daten, Code, externe API).
3. Minimalen Fix implementieren und Nebeneffekte durch Regressionstests prüfen.
4. Root-Cause + Preventive Action im Ergebnisbericht festhalten.

## Safety Guardrails
- Keine blindes Trial-and-Error in produktiven Konfigurationen.
- Keine Deaktivierung von Sicherheits-/Validierungschecks als Dauerlösung.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
