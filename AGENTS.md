# AGENTS.md

## Zweck
Dieses Dokument definiert verbindliche Arbeitsregeln für menschliche und KI-Agenten im Repository **auto-leads**.

## Sicherheitsprinzipien
- **Keine Secrets im Code**: API-Keys, Tokens, Passwörter ausschließlich in `.env`/Secret-Store.
- **Least Privilege**: externe APIs nur mit minimal nötigen Berechtigungen verwenden.
- **Defensive Defaults**: Timeouts, Rate-Limits und Input-Validierung nicht umgehen.
- **Datenschutz by Design**: nur notwendige Lead-Daten erfassen, Aufbewahrung minimieren.
- **Robots/ToS beachten**: Crawler- und API-Nutzung muss rechtlich und vertraglich zulässig sein.

## Test- und Lint-Policy
Bei jeder Änderung an produktivem Code sind lokal auszuführen:

```bash
pytest
black --check .
flake8
```

Ausnahme: ausschließlich Dokumentations-/Kommentaränderungen.

## Do / Don’t
### Do
- bestehende Flask-App-Factory (`app.create_app`) und Blueprints weiterverwenden.
- Konfiguration nur über Umgebungsvariablen und `config.py` erweitern.
- neue Services in `app/services/` kapseln und testbar implementieren.
- bei Architekturänderungen `docs/ARCHITECTURE.md` und ExecPlan aktualisieren.

### Don’t
- keine hardcodierten Pfade, Tokens oder produktiven Endpunkte einchecken.
- keine Umgehung von CSRF-/Rate-Limits in Web/API-Routen.
- keine ungeprüften Breaking Changes ohne Migration/Kommunikation.
- keine direkten Änderungen an Datenmodellen ohne Alembic-Migration.

## Subagent-Policy (Codex)
- Projekt-Subagents liegen in **`.codex/agents/`**.
- Bei komplexen Aufgaben sollen passende Subagents aktiv vorgeschlagen und genutzt werden.
- Für **Security, Review, Testing, Architektur und CI/CD** sind spezialisierte Subagents bevorzugt einzusetzen.
- Parallele Analysen mit mehreren Subagents sind erlaubt, sofern Integrations- und Merge-Punkte klar definiert sind.
- **Schreibende Subagents dürfen niemals gleichzeitig dieselben Dateien bearbeiten**.
- Security-/Reviewer-Agenten sollen bevorzugt **`read-only`** arbeiten.
- Bei großen Features muss vor der Umsetzung ein ExecPlan gemäß `.agent/PLANS.md` erstellt oder aktualisiert werden.

## PR-Mindestanforderungen
- klare Beschreibung von Problem, Lösung, Risiken, Rollback.
- Nachweis der ausgeführten Checks (oder begründete Doku-only-Ausnahme).
- sicherheitsrelevante Auswirkungen explizit dokumentieren.

## Skills-Policy (Codex)
- Projekt-Skills liegen in **`.agents/skills/`**.
- Skills dürfen **nur aufgabenbezogen** geladen werden (kein blindes/globales Laden).
- Bei passenden Aufgaben sind **Security-, Review-, Testing- und CI-Skills** bevorzugt zu verwenden.
- Bei großen Features zuerst ExecPlan gemäß `.agent/PLANS.md` erstellen/aktualisieren.
- Bei Codeänderungen passende Review- und Test-Skills verbindlich anwenden.
- Keine destruktiven Befehle ohne klare fachliche Notwendigkeit und Dokumentation.
- Keine echten Secrets schreiben/lesen, außer für explizite Leak-Prüfungen.
- Scraping-/Lead-Workflows müssen DSGVO, robots.txt, Rate-Limits und Fair-Use beachten.


## Erweiterte Durchsetzungsregeln (verbindlich)

- Skills dürfen ausschließlich passend zur Aufgabe geladen werden; unnötiges/globales Skill-Laden ist unzulässig.
- Bei großen Änderungen (siehe objektive Trigger in `.agent/PLANS.md`) besteht ExecPlan-Pflicht vor Merge.
- Für Security/API/Crawling/DB/CI-relevante Änderungen ist das Multi-Agent-Gate (`docs/MULTI_AGENT_GATE.md`) verpflichtend.
- Reviewer- und Security-Rollen sind bevorzugt `read-only` einzusetzen; schreibende Eingriffe nur mit Begründung.
- Evidence ist Pflicht, nicht optional: Ohne belastbare Nachweise zu Checks, Risiken und Mitigations ist kein Merge zulässig.

## Skill-Routing-Ergänzung (Cloudflare-Vendoring)
- Cloudflare-Referenz-Skills liegen unter `.agents/skills/cloudflare/` und sind bei Aufgaben zu Worker/Perf/Sandbox/Email als primäre Referenz zu nutzen.
- Die Skill-Dateien sind dokumentarische Leitplanken und ersetzen keinen produktiven Flask-App-Code.
