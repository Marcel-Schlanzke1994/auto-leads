# Auto-Leads (lokales Flask Lead-Tool)

Ein lokales Browser-Tool für Lead-Generierung und Lead-Management mit **kostenfreiem OpenStreetMap/Nominatim-Provider (Default)** oder optional offizieller Google Places API (New), Website-Audit (inkl. Impressumserkennung), Dublettenfilter, Lead-Scoring, Dashboard und CSV-Export.

## Features

- Kostenfreie OSM/Nominatim-Suche als Default (kein API-Key erforderlich)
- Optional Google Places Text Search + Place Details (offizielle API, kostenpflichtig je nach Usage)
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
│   │   ├── free_places.py
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
- Für den kostenlosen Standardbetrieb sind keine API-Keys nötig
- Optional: Google Cloud Projekt + Places API (New) + API-Key für den Google-Modus

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Für 100% kostenlosen Betrieb reicht:

```env
PLACES_PROVIDER=osm
```

Optional (Google-Modus):

```env
PLACES_PROVIDER=google_places
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

- Standardmäßig kein externer API-Key nötig (OSM-Modus)
- Google-API-Key nur über `.env` (falls Google-Modus aktiviert)
- CSRF über Flask-WTF
- Rate Limits über Flask-Limiter
- HTTP Timeouts für externe Requests
- SSRF-Schutz: blockiert `localhost`, `127.0.0.1`, private IP-Bereiche, `.local`
- externe Links mit `rel="noopener noreferrer"`

## Kostenhinweis

- **Default (`PLACES_PROVIDER=osm`)**: kostenfrei über OpenStreetMap/Nominatim (bitte faire Nutzung/Rate-Limits beachten).
- **Optional (`PLACES_PROVIDER=google_places`)**: Google Places API ist kostenpflichtig nach Usage/Quota.

## Tests & Qualitätschecks

```bash
pytest
black --check .
flake8
```

