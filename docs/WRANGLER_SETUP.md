# Wrangler Setup (Phase 7)

## Zweck

Diese Doku finalisiert die **optionale** Wrangler-/Cloudflare-Worker-Entwicklung für Auto-Leads, ohne das lokale Flask-System zu ersetzen oder produktiv zu deployen.

## Ordnerstruktur

- `cloudflare/wrangler.example.toml` – sichere Vorlage mit dev/stage/prod-Templates
- `cloudflare/.dev.vars.example` – lokale ENV-Platzhalter ohne Secrets
- `cloudflare/src/*` – bestehender optionaler Worker-Code
- `cloudflare/README.md` – praxisnahe Setup-Anleitung

## Lokale Einrichtung

```bash
cd cloudflare
npm ci
cp .dev.vars.example .dev.vars
cp wrangler.example.toml wrangler.toml
npm run dev
npm run typecheck
```

Hinweis: `wrangler.toml` und `.dev.vars` bleiben gitignored.

## Environment-Vorlagen (dev/stage/prod)

`wrangler.example.toml` enthält:

- `[env.dev]`
- `[env.stage]`
- `[env.prod]`

Alle enthalten nur harmlose Platzhalter (keine realen Domains/IDs/Secrets).

## Secrets und `.dev.vars`

- `.dev.vars.example` enthält nur unkritische Werte (`VERSION`, `AUTO_LEADS_ENV`, `LOG_LEVEL`).
- Echte Secrets ausschließlich via Wrangler Secrets:

```bash
npx wrangler secret put SECRET_NAME
```

- Keine Secrets in Git-Commits.

## Sicherheitsregeln

- Kein Commit von `cloudflare/.dev.vars` oder `cloudflare/wrangler.toml`.
- Keine produktiven Account-/Zone-/Route-IDs in Beispielkonfiguration.
- Keine PII in Logs.
- Kein Bulk-Send und kein Auto-E-Mail-Versand.
- Kein Zugriff auf lokale DB oder Lead-Daten aus Worker-Code.

## Was nicht deployt wird

In Phase 7 erfolgt **kein** echtes Deployment. Optionaler `dry-run` dient nur statischer Prüfung, nicht Rollout.

## Rollback-Hinweise

Da nur optionale Cloudflare-Entwicklungsdateien/Docs ergänzt werden:

1. `git revert <commit>` für vollständigen Rückbau.
2. Lokal erzeugte Dateien (`cloudflare/.dev.vars`, `cloudflare/wrangler.toml`) können jederzeit gelöscht werden.
3. Flask-Betrieb bleibt unverändert, da keine Kopplung eingeführt wird.

## Checks

- Python-Projektchecks:
  - `pytest -q`
  - `black --check .`
  - `flake8`
- Cloudflare optional:
  - `cd cloudflare && npm ci`
  - `cd cloudflare && npm run typecheck`
