# Cloudflare Optional Integration (Foundation)

Dieser Ordner enthält eine **optionale** Cloudflare-Foundation für spätere Edge-Funktionen.

## Wichtige Leitplanken

- Kein Einfluss auf den lokalen Flask-Betrieb.
- Keine Pflichtabhängigkeit auf Cloudflare.
- Keine echten Secrets/IDs/Tokens im Repository.
- Kein E-Mail-Versand, kein Scraping, kein Lead-Datenzugriff.

## Enthalten

- `src/index.ts`: Worker-Prototyp mit `GET /health` und `GET /version`.
- `wrangler.example.toml`: sichere Beispielkonfiguration.
- `package.json` + `tsconfig.json`: lokale Entwicklung/Typecheck.

## Lokale Nutzung (optional)

```bash
cd cloudflare
npm install
npm run dev
npm run typecheck
```

> Hinweis: Für echte Deployments muss eine **lokale** `wrangler.toml` mit echten Werten erzeugt werden.
> Diese Datei darf nicht committed werden.
