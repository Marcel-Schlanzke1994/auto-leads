# Auto-Leads (lokales Flask Lead-Tool)

Ein lokales Browser-Tool für Lead-Generierung und Lead-Management mit offizieller **Google Places API (New)**, Website-Audit (inkl. Impressumserkennung), Dublettenfilter, Lead-Scoring, Dashboard und CSV-Export.

## Features

- Google Places Text Search + Place Details (offizielle API, kein HTML-Scraping)
- Mehrfachsuche für Städte (`Köln, Bonn, Leverkusen`)
- Lokale SQLite-Datenbank
- Dublettenfilter über Domain, Firmenname, Telefonnummer, E-Mail, Place-ID
- Website-Audit inkl. Impressum/Kontakt/About-Scan
- Extraktion von E-Mail, Telefon, Inhaber/GF, Rechtsform (heuristisch)
- Nachvollziehbarer Lead-Score mit Gründen
- Dashboard (Dark UI), Lead-Detailseite, Status-Workflow
- Fortschrittsanzeige für Suchjobs
- CSV-Export
- CSRF-Schutz, Rate-Limiting, SSRF-Schutz gegen private/local Targets

## Projektstruktur

```text
.
├── app.py
├── auto_leads/
│   ├── __init__.py
│   ├── extensions.py
│   ├── forms.py
│   ├── models.py
│   ├── routes/
│   │   ├── api.py
│   │   └── web.py
│   ├── services/
│   │   ├── audit.py
│   │   ├── dedupe.py
│   │   ├── google_places.py
│   │   ├── scoring.py
│   │   └── search_runner.py
│   └── utils.py
├── templates/
├── static/
├── tests/
└── .env.example
```

## Voraussetzungen

- Python 3.11+
- Google Cloud Projekt mit aktivierter **Places API (New)**
- Ein API-Key mit passender Abrechnung/Quota

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

API-Key in `.env` eintragen:

```env
GOOGLE_MAPS_API_KEY=dein_key
```

## Start

```bash
python app.py
```

Dann im Browser öffnen: `http://127.0.0.1:5000`

## Nutzung

1. `/search` öffnen
2. Suchbegriff + Städte eingeben
3. Job starten
4. Fortschritt im Dashboard verfolgen
5. Leads prüfen (`/lead/<id>`), Status setzen, Audit erneut starten
6. Export via `/export/csv`

## API-Endpunkte

- `GET /api/leads`
- `GET /api/leads/<id>`
- `POST /api/search/start`
- `GET /api/search/progress?job_id=<id>`

## Sicherheit

- API-Key nur über `.env`
- CSRF über Flask-WTF
- Rate Limits über Flask-Limiter
- HTTP Timeouts für externe Requests
- SSRF-Schutz: blockiert `localhost`, `127.0.0.1`, private IP-Bereiche, `.local`
- externe Links mit `rel="noopener noreferrer"`

## Google Places Kosten-/Quota-Hinweis

Google Places API ist kostenpflichtig nach Usage/Quota. Prüfe in der Google Cloud Console:

- aktivierte APIs
- Limits (QPS / Tageslimit)
- Billing Budget & Alerts

## Tests & Qualitätschecks

```bash
pytest
black --check .
flake8
```

