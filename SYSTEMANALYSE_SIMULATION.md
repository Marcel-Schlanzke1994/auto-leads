# Systemanalyse und Simulationsprüfung

**Stand der Analyse:** 20. April 2026  
**System:** Auto-Leads (lokales Flask-Tool zur Lead-Generierung über Google Places)

## 1) Hauptfunktionen des Systems

Das System ist ein lokales Web-Tool zur Lead-Generierung, -Anreicherung und -Verwaltung. Kernfunktional startet der Nutzer einen Suchjob mit Suchbegriff und Städten; das System fragt dann über die offizielle Google Places API Place-IDs und Place-Details ab, normalisiert Website-URLs, filtert Dubletten und legt neue Leads in SQLite ab. Zusätzlich wird – sofern eine Website vorhanden ist – ein Website-Audit ausgeführt (Titel/Meta/H1/CTA/Mobile-Signale, Impressums-/Kontaktseiten, E-Mail/Telefon/Legal-Form/Owner-Heuristik), danach erfolgt ein regelbasierter Score mit Begründungen. Die Oberfläche bietet Dashboard, Detailansicht, Status-Workflow, Re-Audit und CSV-Export; API-Endpunkte liefern Leads und Job-Fortschritt. Damit ist der reale Zweck klar: halbautomatische lokale B2B-Lead-Discovery mit technischer Vorqualifizierung.

## 2) Startverhalten (simuliert anhand Initialisierungslogik)

Beim Start (`python app.py`) wird direkt `create_app()` aufgerufen. Dabei werden zunächst Umgebungsvariablen aus `.env` geladen, anschließend Flask inkl. Template-/Static-Pfade initialisiert und zentrale Konfiguration gesetzt (`SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `REQUEST_TIMEOUT`, `GOOGLE_MAPS_API_KEY`, Upload-Limit). Danach werden Datenbank, CSRF-Schutz und Rate-Limiter registriert sowie Web- und API-Blueprints eingebunden. Im App-Context wird `db.create_all()` ausgeführt, d. h. Tabellen werden beim Start automatisch angelegt. Erst danach wird Logging konfiguriert und die App gestartet (Standard: `127.0.0.1:5000`, `debug=False`). Das Startverhalten ist damit robust für lokale Nutzung, birgt aber typische Risiken bei Default-Werten (z. B. unsicherer Fallback-`SECRET_KEY` in Produktionskontexten).

## 3) Abhängigkeiten von externen Diensten/APIs

Ja, es bestehen klare externe Abhängigkeiten:

- **Google Places API (New)**: zwingend erforderlich für Suche/Detailabfrage; ohne `GOOGLE_MAPS_API_KEY` schlägt ein Suchjob gezielt fehl.
- **Beliebige Ziel-Webseiten der gefundenen Firmen**: für das Audit werden HTTP-Requests inkl. Redirect-Following ausgeführt.
- **DNS-Auflösung**: der SSRF-Schutz löst Hostnamen auf, um private/loopback/link-local Ziele zu blockieren.

Nicht extern, aber infrastrukturell relevant: SQLite als lokale Persistenz. Das System hat **keine** OpenAI-/LLM-Abhängigkeit und keine Cloud-Pflicht außerhalb der Google-Places-Nutzung.

## 4) Mögliche Konfigurationsfehler

Typische Fehlkonfigurationen, die in Betrieb oder Sicherheit auffallen können:

- Fehlender/ungültiger `GOOGLE_MAPS_API_KEY` → Suchjobs gehen auf `failed`.
- Nicht gesetzter `SECRET_KEY` → Fallback auf `dev-secret-change-me`; funktional lauffähig, aber sicherheitlich problematisch.
- Unpassender `DATABASE_URL` (Pfad/Rechte) → DB-Initialisierung/Schreiboperationen fehlschlagen.
- Zu niedriger `REQUEST_TIMEOUT` → erhöhte Fehlerquote bei langsamen Zielseiten/APIs.
- Reverse-Proxy-/Container-Betrieb ohne korrektes Client-IP-Handling → Rate-Limits können ungenau greifen.
- Fehlende oder falsche API-Billing-/Quota-Einstellungen bei Google → Teilfehler trotz korrektem Key.

## 5) Sicherheitsaspekte

Positiv ist, dass bereits mehrere Schutzmaßnahmen implementiert sind: CSRF für Form-Requests, Request-Limits via Flask-Limiter und SSRF-Schutz gegen localhost/private Bereiche sowie `.local`-Hosts. Zusätzlich sind Request-Timeouts vorhanden, was bei externen HTTP-Zielen wichtig ist.

Trotzdem sind folgende Punkte kritisch zu beachten:

- Der harte Default für `SECRET_KEY` darf produktiv nicht genutzt werden.
- Externe Web-Audits verarbeiten untrusted HTML/Text; Parser- und Regex-Operationen sollten hinsichtlich Worst-Case-Laufzeit beobachtet werden.
- API-Key-Schutz: Schlüssel nur über `.env`/Secret-Store, nie im Quelltext oder in Logs.
- SQLite ist lokal praktisch, aber bei Mehrbenutzer-/Serverbetrieb funktional und sicherheitlich limitiert.
- Für exponierte Deployments fehlen zusätzliche Härtungen wie HSTS/TLS-Termination, Security Headers auf Reverse-Proxy-Ebene, zentrales Monitoring/Alerting.

## 6) Lokal nutzbar oder zusätzlicher Webserver nötig?

Das System ist **direkt lokal nutzbar**: Start per `python app.py`, Zugriff über Browser auf `http://127.0.0.1:5000`. Ein zusätzlicher Webserver (Nginx/Apache/Caddy) ist für lokale Einzelplatznutzung nicht nötig. Für produktionsnahe oder öffentlich erreichbare Szenarien ist ein vorgelagerter Webserver/Reverse Proxy jedoch empfehlenswert (TLS, Logging, Header-Härtung, Prozessmanagement).

## 7) Bedarf an OpenAI API oder ähnlichem?

Für die vorhandene Kernlogik: **Nein**. Das System nutzt standardmäßig keine OpenAI-API, keine Embeddings und kein LLM-Backend. Erforderlich ist primär ein gültiger Google-Places-Key. Optional könnten LLMs später für Lead-Qualifizierung/Textklassifikation ergänzt werden, sind aber aktuell kein Bestandteil.

## Zusammenfassung mit Empfehlungen für lokale Nutzung

Das System ist ein sauber strukturierter lokaler Flask-Stack mit klarem Lead-Workflow, vernünftigen Basis-Sicherheitsmaßnahmen und nachvollziehbarer Datenverarbeitung. Die wichtigsten Betriebsrisiken liegen in externer API-Abhängigkeit (Google Quota/Billing), Umgebungsvariablenqualität und sicherer Secret-Verwaltung.

Für eine stabile lokale Nutzung empfehle ich:

1. `.env` sauber pflegen: **starker** `SECRET_KEY`, korrekter `GOOGLE_MAPS_API_KEY`, sinnvoller `REQUEST_TIMEOUT`.
2. API-Kosten kontrollieren: Google-Billing aktivieren, Quotas und Alerts setzen.
3. SQLite-Datei und Backup-Strategie definieren (z. B. täglicher Dump).
4. Regelmäßig Tests und Style-Checks fahren (`pytest`, `black --check .`, `flake8`).
5. Logs überwachen (Fehlerrate, Timeouts, API-Statuscodes).
6. Bei Internet-Exponierung Reverse-Proxy mit TLS und Security-Headers nutzen.
7. Für Team-/Mehrnutzerbetrieb mittelfristig auf PostgreSQL + WSGI-Server (gunicorn/uwsgi) migrieren.
