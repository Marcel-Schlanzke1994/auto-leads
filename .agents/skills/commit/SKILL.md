# commit

## Purpose
Sichere Git-Commits mit klarer Historie.

## When to use
- Wenn eine Änderung vollständig validiert wurde.
- Vor PR-Erstellung mit konsistentem Commit-Message-Schema.

## Workflow
1. Arbeitsbaum mit `git status --short` prüfen.
2. Diff thematisch clustern und nur relevante Dateien committen.
3. Commit-Message: `<type>(scope): summary` + Sicherheits-/Risiko-Hinweis im Body.
4. Vor Commit sicherstellen: keine Secrets, keine temporären Artefakte.

## Safety Guardrails
- Keine destruktiven Git-Befehle (`reset --hard`, `clean -fd`, force push) ohne explizite Notwendigkeit.
- Kein Commit von `.env`, Tokens oder personenbezogenen Rohdaten.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
