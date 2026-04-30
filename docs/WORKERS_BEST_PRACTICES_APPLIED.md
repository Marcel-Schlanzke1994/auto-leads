# Workers Best Practices Applied (Phase 6)

## Übersicht

Phase 6 härtet den optionalen Cloudflare-Worker, ohne das lokale Flask-System zu blockieren oder zu ersetzen.

## Umgesetzte Best Practices

- **Typed Contracts**
  - Zentrale Types für Env, Rate-Limit Request/Response und erlaubte Scopes.
- **Zentrale Responses**
  - Einheitliche `jsonOk`/`jsonError` Antworten.
  - Security-Header: `content-type`, `x-content-type-options`.
  - `cache-control: no-store` für state-relevante Antworten.
- **Zentrales Error Handling**
  - Eigener `HttpError` für kontrollierte API-Fehler.
  - Keine Stacktraces im Response-Body.
  - Klare Statuscodes (400/404/405/413/415/500/503).
- **Env/Secrets-Härtung**
  - Optional typisierte ENV (`VERSION`, `OUTREACH_RATE_LIMITER`).
  - Keine Env-Dumps in Responses.
  - Keine harten IDs/Tokens in Konfigurationsbeispielen.
- **Logging/PII**
  - Keine Logs kompletter Requests/Bodys.
  - Nur Route/Status/Error-Code in Fehlerlogs.

## Rate-Limit-Validierung

`POST /rate-limit/check` validiert:

- Methode: nur `POST`
- Content-Type: bei gesetztem Header nur `application/json`
- Body-Größe: defensiv begrenzt
- `scope`: `lead|domain|operation`
- `key`: String, nicht leer, max. Länge (256)
- `limit`: Integer, 1..1000
- `windowSeconds`: Integer, 1..86400

Hinweis: `key` als Hash/ID verwenden, nicht als Klartext-PII.

## Grenzen / Non-Goals

- Kein Worker-Deployment in dieser Phase.
- Keine Cloudflare-Pflichtabhängigkeit.
- Kein E-Mail-/Bulk-Send-Pfad.
- Kein Zugriff auf lokale Flask-Datenbank.

## Manuelle Prüfschritte

1. `cd cloudflare && npm install`
2. `cd cloudflare && npm run typecheck`
3. Optional lokal testen mit `npm run dev`:
   - `GET /health`
   - `GET /version`
   - `POST /rate-limit/check` mit validem/invalidem JSON
