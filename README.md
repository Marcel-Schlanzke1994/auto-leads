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
WEBSITE_FETCH_TIMEOUT=8
WEBSITE_FETCH_MIN_INTERVAL_SECONDS=0
PAGESPEED_TIMEOUT=8
PAGESPEED_MIN_INTERVAL_SECONDS=0
```

## Start (validiert)

```bash
python run.py
```

Dann im Browser öffnen: `http://127.0.0.1:5000`.

## Alternative Starts

```bash
flask --app run:app run --host 127.0.0.1 --port 5000
```

## Security-Hinweise

- **`SECRET_KEY` muss außerhalb von Entwicklung/Test gesetzt werden**; die App startet sonst absichtlich nicht.
- API-Keys (`GOOGLE_MAPS_API_KEY`, `PAGESPEED_API_KEY`) gehören nur in `.env`/Secret-Store, niemals in den Quellcode oder Commits.
- `USER_AGENT` sollte korrekt gepflegt werden, damit externe Dienste Anfragen eindeutig zuordnen können.
- Timeout- und Rate-Limits pro externem Service sind explizit konfigurierbar (Google Places, Website-Fetch, PageSpeed), um Missbrauch und Sperren zu vermeiden.

## Legal / Compliance

- Die Nutzung von Google Places und PageSpeed unterliegt den jeweiligen Google-AGB und Quoten.
- Beim Crawlen fremder Websites sind lokale Gesetze, Nutzungsbedingungen sowie robots-/Rate-Limit-Vorgaben zu beachten.
- Das Tool sollte nur für rechtmäßige B2B-Lead-Prozesse eingesetzt werden; Datenschutzpflichten (z. B. DSGVO) bleiben in Ihrer Verantwortung.

## API-Endpunkte

- `GET /api/leads`
- `GET /api/leads/<id>`
- `POST /api/search/start` (`keyword`, `cities`, optional `target_count`)
- `GET /api/search/progress?job_id=<id>`

## Tests & Qualitätschecks

```bash
pytest
black --check .
flake8
```
