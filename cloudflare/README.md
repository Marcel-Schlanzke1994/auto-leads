# Cloudflare Optional Integration (Foundation + Durable Objects Prototype)

Dieser Ordner enthält eine **optionale** Cloudflare-Foundation für spätere Edge-Funktionen.

## Wichtige Leitplanken

- Kein Einfluss auf den lokalen Flask-Betrieb.
- Keine Pflichtabhängigkeit auf Cloudflare.
- Keine echten Secrets/IDs/Tokens im Repository.
- Kein E-Mail-Versand, kein Scraping, kein Lead-Datenzugriff.
- Kein Zugriff auf lokale DB aus dem Worker.
- Keine personenbezogenen Logs (keine E-Mail-Adressen, Lead-Inhalte, Draft-Texte).

## Worker Best Practices (angewendet)

- Typed Contracts (`src/types.ts`) für Env, Request/Response-Typen.
- Zentrale Response-Helper (`src/responses.ts`) mit Security-Headern.
- Zentrales Error-Handling (`src/errors.ts`) ohne Stacktraces im Response-Body.
- Defensive Request-Validierung für `POST /rate-limit/check` (Methode, Content-Type, Payload-Größe, Feldgrenzen).
- Optionale DO-Bindings: Worker bleibt lauffähig, Cloudflare bleibt optional.

## Endpunkte

- `GET /health`
- `GET /version`
- `POST /rate-limit/check`

### Rate-Limit Hinweis

`key` sollte als **Hash/technische ID** übergeben werden (kein Klartext mit PII wie E-Mail-Adressen).

## Lokale Nutzung (optional)

```bash
cd cloudflare
npm install
npm run dev
npm run typecheck
```

> Kein Deployment in dieser Phase.
