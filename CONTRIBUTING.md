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


## Codex-Review im Pull Request lesen und bewerten
Der Workflow `.github/workflows/codex-code-review.yml` erzeugt für interne Pull Requests automatisch eine Codex-Rückmeldung und schreibt sie als PR-Kommentar.

Ablauf für Reviewer:
1. PR öffnen und den Kommentar **„🤖 Codex Code Review“** suchen.
2. Inhalt als Hinweis nutzen (Risiken, Testideen), nicht als alleinige Freigabegrundlage.
3. Prüfen, ob vorgeschlagene Risiken im Diff tatsächlich zutreffen.
4. Prüfen, ob Testvorschläge im PR umgesetzt sind oder begründet abgelehnt wurden.
5. Bei Fallback-Hinweis (leere Antwort) Artefakt `codex-review` öffnen und bei Bedarf Workflow neu ausführen.

Bewertungsmaßstab:
- **Signalqualität**: Konkrete, dateibezogene Hinweise statt allgemeiner Aussagen.
- **Sicherheitsrelevanz**: Hinweise zu Secrets, Berechtigungen, Input-Validierung und Datenabfluss priorisieren.
- **Umsetzbarkeit**: Vorschläge sollen mit vorhandener Architektur (App-Factory, Blueprints, Services) vereinbar sein.
- **Nachvollziehbarkeit**: Entscheidung im Review dokumentieren (übernommen / verworfen mit kurzer Begründung).

Guardrails im Workflow:
- Kommentar wird nur bei **internen PRs** erstellt (keine Fork-PRs).
- Es werden **keine Secrets** in Logs oder Kommentar ausgegeben.
- Bei leerem Modell-Output wird ein klarer **Fallback-Kommentar** gepostet.

## Review-Checkliste
- [ ] Kein Secret im Diff.
- [ ] Architektur konsistent (Blueprints, Services, Models).
- [ ] Tests ergänzt/angepasst und grün (oder begründete Ausnahme).
- [ ] Linting grün.
- [ ] Datenmodell-/Schemaänderung inkl. Migration.
- [ ] Fehlerfälle, Timeouts, Rate-Limits berücksichtigt.
- [ ] Compliance-Hinweise (DSGVO, robots/ToS) beachtet.
