# Cloudflare Foundation (Phase 2 Skills-Integration)

## Zweck

Diese Cloudflare-Schicht bereitet optionale Edge-Infrastruktur vor, ohne das bestehende lokale Flask-System zu verändern oder zu ersetzen.

## Aktuell implementiert

- Optionaler Ordner `cloudflare/` für Worker-Basisstruktur.
- Worker-Prototyp mit harmlosen Endpunkten:
  - `GET /health`
  - `GET /version`
- Sichere Beispielkonfiguration über `cloudflare/wrangler.example.toml`.
- TypeScript-Basis mit lokalem Typecheck.
- Ergänzte ENV-Platzhalter in `.env.example`.

## Bewusst NICHT implementiert

- Kein Zugriff auf Lead-Daten oder personenbezogene Datensätze.
- Kein Zugriff auf lokale SQLite-DB oder Flask-Models.
- Kein E-Mail-Versand (kein Bulk-Send, kein Auto-Send).
- Kein Scraping/Crawling über den Worker.
- Kein echtes Deployment und keine produktiven Cloudflare-IDs/Tokens im Repo.

## Warum das lokale Flask-System unabhängig bleibt

- Flask bleibt das führende lokale System für Suche, Audit und Outreach-Workflows.
- Die Cloudflare-Komponenten sind vollständig optional und nicht zur Laufzeit gekoppelt.
- Bei deaktivierter Cloudflare-Nutzung gibt es keine Funktionsänderung im aktuellen System.

## ENV-Variablen (Platzhalter)

```env
CLOUDFLARE_ACCOUNT_ID=
CLOUDFLARE_API_TOKEN=
CLOUDFLARE_ZONE_ID=
CLOUDFLARE_WORKER_ENABLED=false
CLOUDFLARE_WORKER_BASE_URL=
```

## Lokale Worker-Kommandos (optional)

```bash
cd cloudflare
npm install
npm run dev
npm run typecheck
```

## Spätere Nutzungsmöglichkeiten

- Edge Health Endpoint
- Rate-Limit-Gateway
- Queue-/Job-Koordination
- Email Provider Adapter
- Web Perf Edge Checks

## Sicherheitsregeln

- Keine Secrets committen.
- Kein Bulk-Send und kein automatischer Versandpfad.
- Kein Zugriff auf lokale DB aus der Cloudflare-Schicht.
- Keine personenbezogenen Logs im Worker.
