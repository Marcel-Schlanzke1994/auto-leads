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


## Verbindliche Planungs- und Agent-Dateien

Bitte nutze für Planung und Umsetzung konsistent die folgenden Dateien:

- `.agent/PLANS.md` als verbindliches Planformat (**Ziele, Milestones, Decision Log, Risks, Progress**).
- `.codex/config.toml` für sichere Agent-Defaults und Qualitäts-Gates.
- `docs/execplans/auto-lead-system-execplan.md` als operativen Master-Plan.

Beiträge sollten diese drei Artefakte nicht widersprüchlich ändern; Plan-/Workflow-Änderungen sind dort nachvollziehbar zu dokumentieren.

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
