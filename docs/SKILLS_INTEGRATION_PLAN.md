# SKILLS_INTEGRATION_PLAN

## Übernommene Skills
Unter `.agents/skills/cloudflare/` wurden folgende Skill-Pakete als Referenz integriert:
- `agents-sdk`
- `cloudflare`
- `durable-objects`
- `sandbox-sdk`
- `web-perf`
- `workers-best-practices`
- `wrangler`
- `cloudflare-email-service`

## Zielbild im Auto-Leads-System
Das bestehende Flask-System bleibt führend. Die Skills dienen als Leitfaden für optionale, schrittweise Erweiterungen.

### A) Agents SDK Skill (Planung)
Geplante lokale Agentenstruktur (ohne sofortige produktive Aktivierung):
- `services/agents/`
- `SEOAgent`
- `AuditAgent`
- `ComplianceAgent`
- `OutreachAgent`
- `Orchestrator`

### B) Cloudflare Skill (Planung)
Optionale Infrastrukturvorbereitung:
- `cloudflare/`
- `cloudflare/README.md`
- `cloudflare/wrangler.example.toml`

### C) Durable Objects Skill (Planung)
- Spätere optionale State-/Queue-/Rate-Limit-Schicht.
- Keine Pflichtabhängigkeit für den lokalen Betrieb.

### D) Sandbox SDK Skill (Planung)
Sicherheitsvorgaben für Website-/Browser-Analyse:
- URL-Validierung
- SSRF-Schutz
- harte Timeouts

### E) Web Perf Skill (Planung)
- Erweiterung bestehender Audit-Logik um Core Web Vitals und Performance-Signale.

### F) Workers Best Practices Skill (Planung)
- Anwendung nur auf künftige Worker-Prototypen unter `cloudflare/`.

### G) Wrangler Skill (Planung)
- Sichere Beispielkonfigurationen ohne echte IDs, Tokens, Secrets.

### H) Cloudflare Email Service Skill (Planung)
- Optionaler `EmailProvider` als Erweiterungspunkt.
- Standard bleibt `debug/local`.
- Kein Bulk-Send.
- Versand nur mit manueller Freigabe, Opt-out/Blacklist-Checks und Logging.

## Was ist nur dokumentierte Architektur?
- Alle vendored Skill-Dateien unter `.agents/skills/cloudflare/`.
- Cloudflare-Ordner und Wrangler-Example-Datei als Referenz-/Bootstrap-Artefakte.

## Was bekommt konkrete App-Erweiterungen (spätere Schritte)?
- Agenten-Orchestrierung in separaten Services (`services/agents/`).
- Audit-Erweiterung (Web-Performance) hinter Feature-Flags.
- Optionaler EmailProvider mit sicherem Default (kein aktiver Massenversand).

## Risikoanalyse
- **Konfigurationsrisiko**: versehentliches Aktivieren externer Cloudflare-Integrationen.
  - Mitigation: nur `example`-Configs, keine produktiven Defaults.
- **Sicherheitsrisiko (SSRF/Fetch)** bei Website-Analyse.
  - Mitigation: Validierung, Allow-/Deny-Regeln, Timeouts.
- **Compliance-Risiko (Outreach/Email)**.
  - Mitigation: manuelle Freigabe, OptOut-/Blacklist-Prüfung, Audit-Logging.
- **Wartungsrisiko** durch vendored Referenzen.
  - Mitigation: dokumentierter Update-Prozess und SHA-Pinning in `docs/SKILLS_VENDORING.md`.

## Akzeptanzkriterien
- Bestehende Flask-Routen/Models/Services/Templates bleiben unverändert funktionsfähig.
- Keine Secrets oder produktiven Cloudflare-Credentials im Repository.
- Vendored Skills liegen ausschließlich unter `.agents/skills/cloudflare/`.
- Dokumentation (`SKILLS_VENDORING`, `SKILLS_INTEGRATION_PLAN`) ist vollständig und nachvollziehbar.
- Lokaler Start und bestehende Tests bleiben lauffähig.
