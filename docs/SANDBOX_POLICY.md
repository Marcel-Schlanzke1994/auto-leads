# Sandbox Policy (Phase 4 Skills-Integration)

## Warum diese Policy nötig ist

Externe Website-Analysen (Audit, SEO, spätere Browser-/Playwright-Jobs) sind ein SSRF- und Stabilitätsrisiko, wenn Eingabe-URLs ungeprüft verarbeitet werden. Diese Policy ergänzt das bestehende System additiv mit sicheren Defaults.

## Verhinderte Risiken

- SSRF auf interne Dienste
- Zugriff auf lokale Dienste (`localhost`, Loopback)
- Zugriff auf private/interne Netzbereiche
- Missbrauch über unerwartete URL-Schemes
- Endlose/zu große Analysejobs durch harte Limits

## Implementierte URL-Regeln

`validate_external_url(url)` erzwingt zentral:

- nur `http` und `https`
- keine leeren URLs
- keine relativen URLs
- blockierte Schemes: `file`, `ftp`, `data`, `javascript`, `chrome`, `ws`, `wss`
- blockiert Credentials in URL (`user:pass@host`)
- Hostname-Normalisierung inkl. IDN/Punycode (`idna`)
- Port-Validierung (1..65535)
- blockiert `localhost` (außer `allow_localhost=True`)
- blockiert private/interne Ziele via IP/DNS-Check

## DNS-/IP-Absicherung

- Hostname wird (standardmäßig) aufgelöst.
- Jede aufgelöste IP wird gegen private/interne Bereiche geprüft.
- DNS-Fehler führen zu `SandboxPolicyError`.
- Für Tests ist Resolver-Injection vorgesehen (`resolver=...`).

## Zentrale Limits (sichere Defaults)

- `REQUEST_TIMEOUT_SECONDS = 8`
- `MAX_REDIRECTS = 3`
- `MAX_PAGES_PER_LEAD = 5`
- `MAX_SCREENSHOTS_PER_LEAD = 3`
- `MAX_RESPONSE_BYTES = 2_000_000`
- `MAX_ANALYSIS_SECONDS = 30`

## Nutzung in bestehenden Services

- Minimal integriert in `website_fetcher_service.normalize_url`.
- Bestehende Audit-Pipeline bleibt funktional; es wird nur die URL-Validierung zentralisiert.
- Keine Cloudflare-Pflichtabhängigkeit, kein Deployment, kein Versandpfad.

## Leitplanke für spätere Playwright-Jobs

Spätere Browser-/Playwright-Analysen sollen vor jedem Job:

1. Ziel-URL via `validate_external_url` prüfen.
2. Zeit-/Umfangs-Limits aus `SandboxPolicy` anwenden.
3. Redirect-Ziel erneut validieren.
4. `allow_localhost` nur explizit in lokalen Testmodi aktivieren.

## DEV_MODE-Hinweis

`allow_localhost=True` ist ausschließlich für lokale Entwicklung/Tests vorgesehen und darf nie Produktions-Default sein.

## Beispiele

Erlaubt:

- `https://example.com`
- `http://example.com`

Blockiert:

- `file:///etc/passwd`
- `javascript:alert(1)`
- `http://localhost`
- `http://127.0.0.1`
- `https://user:pass@example.com`
