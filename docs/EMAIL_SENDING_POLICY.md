# Email Sending Policy (Phase 8)

## Grundprinzip

Auto-Leads nutzt standardmäßig den **DebugEmailProvider**. Dieser sendet keine echten E-Mails und liefert nur eine Preview.

## Sicherheitsregeln

- **Kein Bulk-Send**: keine `send_many`/`send_bulk`/`send_all` APIs.
- Versand nur als **Einzelversand**.
- Versand nur mit expliziter **manueller Freigabe**.
- Keine automatische Versandroute in dieser Phase.
- Opt-out/Blacklist/Compliance müssen den Versand blockieren.

## SendPolicy (zentrale Prüfungen)

`validate_email_send_allowed(...)` blockiert u. a. bei:

- fehlender `manual_approval=True`
- fehlender/ungültiger Empfängeradresse
- nicht freigegebenem Draft (`status != approved`)
- `outreach_allowed=False` (falls vorhanden)
- nicht erlaubtem `outreach_status` (falls vorhanden)
- gesetzten Block-Flags wie `opt_out`/`blacklisted` (falls vorhanden)
- optionalem send_count-Limit (falls Felder vorhanden)

## Provider-Konfiguration

Default:

- `EMAIL_PROVIDER` fehlt oder `debug` -> DebugEmailProvider (Preview only)

Optional Cloudflare:

- `EMAIL_PROVIDER=cloudflare`
- `CLOUDFLARE_EMAIL_PROVIDER_ENABLED=true`
- notwendige Secrets/ENV gesetzt

Hinweis: In Phase 8 ist Cloudflare als **sicherer Adapter/Stub** vorbereitet. Keine automatische Aktivierung, keine Bulk-Logik.

## Secrets

- Keine Secrets im Repo.
- Lokal via `.env`.
- Für Worker/Cloudflare via `wrangler secret put ...`.

## Lokale Checks

```bash
pytest -q
black --check .
flake8
cd cloudflare && npm ci
cd cloudflare && npm run typecheck
```

## Rechtlicher Hinweis

Kein automatisierter Kaltakquise-Massenversand. Nutzung nur rechtskonform (DSGVO, ToS, Opt-out/Blacklist respektieren).

## Rollback

- Feature kann via `EMAIL_PROVIDER=debug` sofort neutralisiert werden.
- Commit-Rückbau via `git revert <commit>`.
