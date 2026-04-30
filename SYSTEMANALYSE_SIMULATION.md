# Systemanalyse und Simulationsprüfung

**Stand der Analyse:** 28. April 2026  
**Last verified against commit:** `e7dc57e`  
**System:** Auto-Leads (lokales Flask-Tool zur Lead-Generierung über Google Places)

## 1) Hauptfunktionen des Systems

Das System ist ein lokales Web-Tool zur Lead-Generierung, -Anreicherung und -Verwaltung. Kernfunktional startet der Nutzer einen Suchjob mit Suchbegriff und Städten; das System fragt dann über die offizielle Google Places API Place-IDs und Place-Details ab, normalisiert Website-URLs, filtert Dubletten und legt neue Leads in SQLite ab. Zusätzlich wird – sofern eine Website vorhanden ist – ein Website-Audit ausgeführt (Titel/Meta/H1/CTA/Mobile-Signale, Impressums-/Kontaktseiten, E-Mail/Telefon/Legal-Form/Owner-Heuristik), danach erfolgt ein regelbasierter Score mit Begründungen. Die Oberfläche bietet Dashboard, Detailansicht, Status-Workflow, Re-Audit und CSV-Export; API-Endpunkte liefern Leads und Job-Fortschritt.

## 2) Startverhalten (konsistent zur aktuellen Runtime)

**Einstiegspunkt ist `run.py`**: Beim Start (`python run.py`) wird `create_app()` aus `app` importiert und die Flask-App erzeugt. Anschließend startet `app.run(...)` mit `APP_HOST` und `APP_PORT` aus der Konfiguration sowie `debug=False`.

In `app.create_app()` erfolgt danach die eigentliche Initialisierung:

- `.env` wird geladen (`load_dotenv()`).
- Konfiguration kommt aus `config.py` (`app.config.from_object(Config)`), optional ergänzt durch `test_config`.
- Für Tests gilt ein spezieller Fallback-`SECRET_KEY` (`test-secret-key`) nur bei `TESTING=True`.
- `_validate_security_config(app)` wird **vor** der restlichen App-Initialisierung ausgeführt.
- Extensions werden registriert (`db`, `csrf`, `limiter`, `migrate`).
- Blueprints werden eingebunden: `dashboard`, `leads`, `jobs`, `export`, `api`, `web_compat`.
- Für den API-Blueprint wird CSRF optional ausgenommen (`API_REQUIRE_CSRF=False` als Default).
- Logging wird konfiguriert.

Wichtig zur Abgrenzung: Es gibt aktuell **kein** automatisches `db.create_all()` beim normalen Start in `create_app()`.

## 3) Externe Abhängigkeiten

- **Google Places API (New)**: zwingend für Such- und Detailabfragen.
- **Ziel-Webseiten der Leads**: für Website-Audit und Extraktion.
- **DNS-Auflösung**: Bestandteil des SSRF-Schutzes.

Nicht extern, aber runtime-relevant: SQLite (Default) mit SQLAlchemy/Alembic.

## 4) Konsistenz-Check der angefragten Punkte

### 4.1 `run.py` als Einstiegspunkt

Erfüllt. Der operative Startpfad ist `run.py` → `create_app()` → `app.run(...)`.

### 4.2 `app/__init__.py::_validate_security_config`

Erfüllt. In Nicht-Dev-/Nicht-Test-Kontexten wird ein fehlender oder Platzhalter-`SECRET_KEY` explizit per `RuntimeError` blockiert. Dadurch existiert **kein unsicherer Produktions-Default**. Der Test-Fallback (`test-secret-key`) gilt nur unter `TESTING`.

### 4.3 Blueprint-/Service-Struktur vs. `docs/ARCHITECTURE.md`

Konsistent. Die in der Architektur dokumentierten Blueprints (`dashboard`, `leads`, `jobs`, `export`, `api`, `web_compat`) und die Service-Gruppen unter `app/services/` entsprechen der aktuellen Struktur.

## 5) Sicherheitsaspekte (Status)

Positiv vorhanden:

- CSRF-Schutz für Web-Formularrouten.
- Rate-Limiting via Flask-Limiter.
- SSRF-Schutz im Audit-Workflow.
- Produktions-Schutz für `SECRET_KEY` via `_validate_security_config`.

Weiterhin relevant:

- API-Write-Endpoints bleiben in Verantwortung von Token-Auth, restriktiven Limits und Input-Validierung (CSRF ist für API standardmäßig ausgenommen).
- Secrets weiterhin ausschließlich über `.env`/Secret-Store.

## 6) Betriebsmodus lokal vs. produktionsnah

- **Lokal:** direkt per `python run.py` nutzbar.
- **Produktionsnah/öffentlich:** Reverse Proxy + TLS + Header-Härtung + Monitoring empfohlen.

---

## 7) Simulierte Vollprüfung (Konsistenzfokus)

**Durchgeführt am:** 28. April 2026 (UTC)  
**Kontext:** Struktur-/Konfigurationskonsistenz anhand Code und Architektur-Doku.

### Ergebnis

- Einstiegspunkt: korrekt auf `run.py`.
- Security-Validierung: vorhanden und produktionssicher bzgl. `SECRET_KEY`-Defaults.
- Architektur-Doku: konsistent zur aktuellen Blueprint-/Service-Organisation.

### Kurzfazit

Die Analyse ist auf dem aktuellen Stand und mit den angefragten technischen Referenzen konsistent.
