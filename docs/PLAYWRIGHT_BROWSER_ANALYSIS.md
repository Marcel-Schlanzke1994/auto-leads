# Playwright Browser-/Kontaktformular-Analyse (Phase 9)

Optionales Feature für Kontaktseiten- und Formularanalyse. Standardmäßig deaktiviert.

## Installation (optional)
- `pip install playwright`
- `python -m playwright install chromium`

## ENV Flags
- `PLAYWRIGHT_ANALYSIS_ENABLED=false`
- `PLAYWRIGHT_SCREENSHOTS_ENABLED=false`
- `PLAYWRIGHT_BROWSER=chromium`
- `PLAYWRIGHT_MAX_PAGES_PER_LEAD=5`

## Sicherheitsmodell
- Jede Ziel-URL wird über `validate_external_url(...)` geprüft.
- Nur `http/https`, keine Credentials, keine privaten/internal Hosts.
- Limits aus Sandbox-Policy: `MAX_PAGES_PER_LEAD`, `MAX_SCREENSHOTS_PER_LEAD`, `MAX_ANALYSIS_SECONDS`.

## Verhalten
- Erkennt Kontaktseiten über Link-Scoring (Kontakt/Contact/Anfrage/...)
- Erkennt Formulare und klassifiziert Felder (`email`, `name`, `phone`, `message`, ...)
- Setzt Warnungen (Captcha/Consent/fehlende Felder)
- Erstellt nur Draft-Empfehlungstext

## Explizit ausgeschlossen
- Kein Auto-Fill
- Kein Auto-Submit
- Kein Captcha-Bypass
- Kein automatischer Versand

## Datenschutz & Grenzen
- Screenshots sind optional und standardmäßig aus.
- Manuelle Prüfung bleibt erforderlich.
