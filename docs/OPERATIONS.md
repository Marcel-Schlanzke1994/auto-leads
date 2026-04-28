# Operations

## Lokaler Betrieb

### Voraussetzungen
- Python 3.11+
- virtuelle Umgebung
- installierte Abhängigkeiten aus `requirements.txt`

### Start
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
flask db upgrade
python run.py
```

## Monitoring & Logging
- App-Logging wird beim Start zentral konfiguriert (`logging.basicConfig`).
- Empfohlen:
  - Pro Suchjob Korrelation über `job_id`
  - Warnungen für Timeouts/Rate-Limits extern markieren
  - Fehlerlogs ohne personenbezogene Daten/Secrets

### Operative Kernmetriken
- Job-Durchlaufzeit (p50/p95)
- Fehlerrate pro externem Dienst
- Verhältnis Rohdaten → deduplizierte Leads
- Export-Erfolgsquote

## Backup / Restore

### Backup (SQLite)
- App stoppen oder Schreibzugriffe pausieren.
- SQLite-Datei sichern (z. B. `leads.db`).
- Versioniertes Backup mit Zeitstempel ablegen.

### Restore
- App stoppen.
- Aktuelle DB sichern (Failsafe).
- Backup-Datei als aktive `leads.db` zurückspielen.
- `flask db upgrade` ausführen, danach Smoke-Test (`/`, `/dashboard`, `/api/leads`).

## Störungsbehebung (Kurzleitfaden)
1. **API-Fehler/Quota**: Key/Quota prüfen, Intervall/Backoff erhöhen.
2. **Crawler-Timeouts**: `WEBSITE_FETCH_TIMEOUT`, `CRAWL_MAX_PAGES` kalibrieren.
3. **Leere Ergebnisse**: Suchbegriffe, Städte, Provider-Konfig validieren.
4. **Instabile Exporte**: Datenschema/Feldmapping und Encoding prüfen.
