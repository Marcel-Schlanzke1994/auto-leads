# Web Perf Audit Erweiterung (Phase 5)

## Zweck
Additive Erweiterung des bestehenden Website-Audits um strukturierte Performance-Signale.

## Datenquellen
- Bestehende Fetch-Pipeline (`website_fetcher_service`)
- Optionale PageSpeed API (`PAGESPEED_API_KEY`)
- Lokale HTML/Header-Heuristiken ohne aggressive Zusatz-Crawls

## PageSpeed optional
Ohne API-Key läuft das System weiter und nutzt lokale Signale/Fallbacks.

## Lokale Heuristiken
- Kompression (`content-encoding`)
- Cache-Hinweise (`cache-control`, `etag`, `last-modified`)
- Render-Blocking-Risiko aus CSS/JS-Indikatoren
- Bildoptimierungs-Risiko (fehlende width/height, lazy-loading Hinweise)
- Mobile-Risiko via viewport + Ressourcenlast
- HTML-Größe im Rahmen von Sandbox-Limits (`MAX_RESPONSE_BYTES`)

## Score-Auswirkung
Additive technische Regeln im Lead-Score, z. B. niedriger Perf-Score, fehlende Kompression, hohe Render-/Image-/Mobile-Risiken.

## SandboxPolicy-Anbindung
Nutzt weiterhin die bestehende URL-Validierung und macht keine zusätzlichen unsicheren Netzwerkpfade auf.

## Grenzen
- Kein Full-Lab-Test lokal
- Keine zusätzlichen Requests pro Ressource in dieser Phase
- PSI-Metriken abhängig von API-Verfügbarkeit

## Beispiel-Ergebnis
Siehe `web_perf`-Block in `raw_pagespeed_json` eines `AuditResult`.
