# Contributing

Vielen Dank für Beiträge zu **auto-leads**.

## Branching-Modell
- `main`: stabiler Integrationsstand.
- Feature-Branches: `feat/<kurzbeschreibung>`
- Bugfix-Branches: `fix/<kurzbeschreibung>`
- Chore/Doku: `chore/<thema>`, `docs/<thema>`

## Commit-Konvention
Empfohlenes Format (Conventional Commits):
- `feat: ...`
- `fix: ...`
- `docs: ...`
- `refactor: ...`
- `test: ...`
- `chore: ...`

Beispiel:
`feat: add retry handling for google places pagination`

## Entwicklungsablauf
1. Branch erstellen.
2. Änderungen klein und fokussiert halten.
3. Bei Codeänderungen lokal prüfen:
   ```bash
   pytest
   black --check .
   flake8
   ```
4. Doku aktualisieren (README/ARCHITECTURE/OPERATIONS/ROADMAP), falls relevant.
5. PR mit Risiko- und Rollback-Hinweis öffnen.

## Review-Checkliste
- [ ] Kein Secret im Diff.
- [ ] Architektur konsistent (Blueprints, Services, Models).
- [ ] Tests ergänzt/angepasst und grün (oder begründete Ausnahme).
- [ ] Linting grün.
- [ ] Datenmodell-/Schemaänderung inkl. Migration.
- [ ] Fehlerfälle, Timeouts, Rate-Limits berücksichtigt.
- [ ] Compliance-Hinweise (DSGVO, robots/ToS) beachtet.
