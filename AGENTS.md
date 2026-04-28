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

## PR-Mindestanforderungen
- klare Beschreibung von Problem, Lösung, Risiken, Rollback.
- Nachweis der ausgeführten Checks (oder begründete Doku-only-Ausnahme).
- sicherheitsrelevante Auswirkungen explizit dokumentieren.
