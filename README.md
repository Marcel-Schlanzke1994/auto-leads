# Auto-Leads (lokales Flask Lead-Tool)

Ein lokales Browser-Tool für Lead-Generierung und Lead-Management mit offizieller **Google Places API (New)** als Primärquelle, Website-Audit (inkl. Impressumserkennung), Dublettenfilter, Lead-Scoring, Dashboard und CSV-Export.

## Features

- Konfiguration vollständig über `.env` (`python-dotenv`)
- Google Places Text Search + Place Details (offizielle API)
- Pagination/iterative Folgeabfragen für große Suchläufe
- Zielanzahl pro Job (Standard 1000, max. 1000 neue Leads)
- Mehrfachsuche für Städte (`Köln, Bonn, Leverkusen`)
- Lokale SQLite-Datenbank
- Dublettenfilter über Domain, Firmenname, Telefonnummer, E-Mail, Place-ID
- Website-Audit inkl. Impressum/Kontakt/About-Scan
- Extraktion von E-Mail, Telefon, Inhaber/GF, Rechtsform (heuristisch)
- Nachvollziehbarer Lead-Score mit Gründen
- Dashboard (Dark UI), Lead-Detailseite, Status-Workflow
- Fortschrittsanzeige für Suchjobs inkl. Rohdaten/Dubletten/Filter
- CSV-Export inkl. Google-Rating/Review-Count/Score-Gründe
- CSRF-Schutz, Rate-Limiting, SSRF-Schutz gegen private/local Targets

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Datenbank initialisieren / migrieren

```bash
flask db upgrade
```

> Hinweis: Standard-URL ist `sqlite:///leads.db`.

## `.env`

```env
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=replace-with-a-long-random-secret
DATABASE_URL=sqlite:///leads.db
APP_HOST=127.0.0.1
APP_PORT=5000
REQUEST_TIMEOUT=8
USER_AGENT=auto-leads/3.0 (+website-audit)
SEARCH_DEFAULT_CITIES=Köln, Bonn, Leverkusen
SEARCH_MAX_TARGET_COUNT=1000
SEARCH_TEXT_PAGE_LIMIT=60
SEARCH_MAX_RAW_RESULTS=3000
CRAWL_MAX_PAGES=10
CRAWL_DELAY_SECONDS=0.1
PLACES_PROVIDER=google_places
GOOGLE_MAPS_API_KEY=PASTE_YOUR_NEW_GOOGLE_API_KEY_HERE
PAGESPEED_API_KEY=
GOOGLE_PLACES_TIMEOUT=8
GOOGLE_PLACES_MIN_INTERVAL_SECONDS=2.1
GOOGLE_PLACES_RETRY_MAX_ATTEMPTS=4
GOOGLE_PLACES_RETRY_BACKOFF_BASE=0.5
GOOGLE_PLACES_RETRY_MAX_DELAY=8
GOOGLE_PLACES_RETRY_JITTER=0.3
WEBSITE_FETCH_TIMEOUT=8
WEBSITE_FETCH_MIN_INTERVAL_SECONDS=0
PAGESPEED_TIMEOUT=8
PAGESPEED_MIN_INTERVAL_SECONDS=0
API_AUTH_TOKEN=change-me-to-a-long-random-token
```

## Start (validiert)

```bash
python run.py
```

Hinweis: `python run.py` verwendet `APP_HOST` und `APP_PORT` aus Ihrer `.env` (z. B. `127.0.0.1` und `5000`).

Dann im Browser öffnen: `http://127.0.0.1:5000` (bzw. entsprechend Ihrer `APP_HOST`/`APP_PORT`-Werte).

## Alternative Starts

```bash
flask --app run.py run
```

## Security-Hinweise

- **`SECRET_KEY` muss außerhalb von Entwicklung/Test gesetzt werden**; die App startet sonst absichtlich nicht.
- API-Keys (`GOOGLE_MAPS_API_KEY`, `PAGESPEED_API_KEY`) gehören nur in `.env`/Secret-Store, niemals in den Quellcode oder Commits.
- `USER_AGENT` sollte korrekt gepflegt werden, damit externe Dienste Anfragen eindeutig zuordnen können.
- Timeout- und Rate-Limits pro externem Service sind explizit konfigurierbar (Google Places, Website-Fetch, PageSpeed), um Missbrauch und Sperren zu vermeiden.
- Google-Places-Retries (429/5xx/Netzwerkfehler) sind über `GOOGLE_PLACES_RETRY_MAX_ATTEMPTS`, `GOOGLE_PLACES_RETRY_BACKOFF_BASE`, `GOOGLE_PLACES_RETRY_MAX_DELAY` und `GOOGLE_PLACES_RETRY_JITTER` steuerbar.

## Legal / Compliance

- Die Nutzung von Google Places und PageSpeed unterliegt den jeweiligen Google-AGB und Quoten.
- Beim Crawlen fremder Websites sind lokale Gesetze, Nutzungsbedingungen sowie robots-/Rate-Limit-Vorgaben zu beachten.
- Das Tool sollte nur für rechtmäßige B2B-Lead-Prozesse eingesetzt werden; Datenschutzpflichten (z. B. DSGVO) bleiben in Ihrer Verantwortung.

## API-Endpunkte

- `GET /api/leads`
- `GET /api/leads/<id>`
- `POST /api/search/start` (`keyword`, `cities`, optional `target_count`)
- `GET /api/search/progress?job_id=<id>`

### API-Sicherheitsstrategie (explizit)

Für den API-Blueprint ist CSRF **bewusst deaktiviert**. Stattdessen gilt für schreibende
Endpoints (aktuell: `POST /api/search/start`) ein API-Contract mit
Token-Authentifizierung, strengeren Limits und Input-Validierung:

- Authentifizierung per Header `X-API-Key` gegen `API_AUTH_TOKEN`.
- Ohne/mit falschem Token: `401 {"error":"unauthorized"}`.
- Wenn `API_AUTH_TOKEN` nicht konfiguriert ist: `503 {"error":"api auth token is not configured"}`.
- Strikteres Rate-Limit für den Start-Endpoint: `5/minute;30/hour`.
- Request muss JSON sein (`Content-Type: application/json`) und ein JSON-Objekt enthalten.
- Validierung:
  - `keyword` erforderlich, max. 120 Zeichen.
  - `cities` erforderlich, 1 bis 25 Städte (kommagetrennt).
  - `target_count` muss Integer sein; Werte werden auf `1..SEARCH_MAX_TARGET_COUNT` begrenzt.

Beispiel:

```bash
curl -X POST http://127.0.0.1:5000/api/search/start \
  -H "Content-Type: application/json" \
  -H "X-API-Key: $API_AUTH_TOKEN" \
  -d '{"keyword":"Elektriker","cities":"Köln, Bonn","target_count":250}'
```

## Tests & Qualitätschecks

```bash
pytest
black --check .
flake8
```

## Outreach-CRM (ergänzend)

- Bestehende Leads können auf der Detailseite um Outreach-Informationen ergänzt werden:
  - Kontaktstatus, Drafts, ContactAttempts, Callback, Opt-Out/Blacklist.
- Das System erzeugt nur Drafts (E-Mail/Kontaktformular/Telefonskript), kein automatischer Versand.
- Opt-Out/Blacklist blockiert die Draft-Erzeugung und markiert Kontakte als gesperrt.
- CSV-Export enthält zusätzliche Outreach-Spalten wie `contact_status`, `last_contact_at`, `next_callback_at`, `outreach_allowed`, `draft_count`, `attempt_count`.
- Nach Pull neuer Änderungen Migrationen ausführen:

```bash
flask db upgrade
```


## Planungs- und Agent-Workflow

Für einen einheitlichen Ablauf zwischen Entwicklern und Agenten gelten folgende Steuerdateien:

- `.agent/PLANS.md`: verbindliches Planformat mit den Abschnitten **Ziele, Milestones, Decision Log, Risks, Progress**.
- `.codex/config.toml`: sichere Codex-Defaults (u. a. Secret-Handling, Sandbox/Approval-Strategie, bevorzugte Qualitäts-Checks).
- Operativer Master-Plan: `docs/execplans/auto-lead-system-execplan.md`.

Änderungen sollten immer entlang des ExecPlans geplant und in den oben genannten Dateien konsistent dokumentiert werden.

## Optional Cloudflare Worker Foundation

Die Cloudflare-Schicht ist aktuell eine **optionale Vorbereitung** und hat keinen Einfluss auf das lokale Flask-System.

Details: `docs/CLOUDFLARE_FOUNDATION.md`

```bash
cd cloudflare
npm install
npm run dev
npm run typecheck
```

