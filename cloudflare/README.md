# Cloudflare Optional Integration (Wrangler Finalization)

Dieser Ordner enthält eine **optionale** Cloudflare-Worker-Entwicklungsumgebung.
Das lokale Flask-System bleibt führend und unverändert lauffähig.

## Wichtige Leitplanken

- Kein Einfluss auf den lokalen Flask-Betrieb.
- Keine Pflichtabhängigkeit auf Cloudflare.
- Keine echten Secrets/IDs/Tokens im Repository.
- Kein E-Mail-Versand, kein Bulk-Send, kein Auto-Send.
- Kein Zugriff auf lokale DB aus dem Worker.
- Kein Scraping/Crawling über den Worker.

## Endpunkte (bestehend)

- `GET /health`
- `GET /version`
- `POST /rate-limit/check`

## Setup (optional, lokal)

```bash
cd cloudflare
npm ci
cp .dev.vars.example .dev.vars
cp wrangler.example.toml wrangler.toml
npm run dev
npm run typecheck
```

## Warum `wrangler.toml` ignoriert wird

`wrangler.toml` enthält projektspezifische lokale Werte (z. B. IDs/Routes/Env-Anpassungen) und bleibt deshalb **gitignored**.
Bitte nur `wrangler.example.toml` als sichere Vorlage versionieren.

## Secrets sicher setzen

Echte Secrets niemals in `.dev.vars.example`, `wrangler.example.toml` oder Git-Commits ablegen.
Für Cloudflare-Secrets lokal/remote:

```bash
npx wrangler secret put SECRET_NAME
```

## Commit-Schutz

Nicht committen:

- `cloudflare/.dev.vars`
- `cloudflare/wrangler.toml`

## Safe Local Testing

- `npm run dev` startet lokale Worker-Entwicklung.
- `npm run typecheck` prüft TS-Typen CI-kompatibel.
- `npm run dry-run` ist optional und führt **kein echtes Deployment** aus.

## Grenzen / Non-Goals

- Kein produktives Deployment in dieser Phase.
- Kein automatischer E-Mail-Versand.
- Kein Bulk-Send.
- Kein DB-Zugriff aus Worker-Kontext.
