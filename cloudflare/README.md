# Cloudflare Optional Integration (Foundation + Durable Objects Prototype)

Dieser Ordner enthält eine **optionale** Cloudflare-Foundation für spätere Edge-Funktionen.

## Wichtige Leitplanken

- Kein Einfluss auf den lokalen Flask-Betrieb.
- Keine Pflichtabhängigkeit auf Cloudflare.
- Keine echten Secrets/IDs/Tokens im Repository.
- Kein E-Mail-Versand, kein Scraping, kein Lead-Datenzugriff.
- Durable Objects sind in dieser Phase nur Prototyp/Architektur.

## Enthalten

- `src/index.ts`: Worker-Prototyp mit:
  - `GET /health`
  - `GET /version`
  - `POST /rate-limit/check` (Prototyp)
- `src/rate_limit_object.ts`: Durable Object `OutreachRateLimiter`.
- `wrangler.example.toml`: sichere Beispielkonfiguration inkl. Durable-Object-Binding.
- `package.json` + `tsconfig.json`: lokale Entwicklung/Typecheck.

## Lokale Nutzung (optional)

```bash
cd cloudflare
npm install
npm run dev
npm run typecheck
```

> Hinweis: Worker-Tests lokal nur nach `npm install`.

## Beispiel für Rate-Limit-Prototyp

```bash
curl -X POST "http://127.0.0.1:8787/rate-limit/check" \
  -H "Content-Type: application/json" \
  -d '{
    "scope": "domain",
    "key": "example.com-hash-or-id",
    "limit": 5,
    "windowSeconds": 60
  }'
```

Beispielantwort:

```json
{
  "allowed": true,
  "remaining": 4,
  "resetAt": "2026-04-28T12:00:00.000Z",
  "scope": "domain",
  "key": "example.com-hash-or-id"
}
```

## Sicherheit / Produktivnutzung

- Kein produktiver Einsatz ohne eigene Cloudflare-Konfiguration.
- Keine echten IDs/Tokens im Beispiel.
- Kein automatischer Versandpfad und kein Bulk-Send.
