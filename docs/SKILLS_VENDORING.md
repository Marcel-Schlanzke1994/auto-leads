# SKILLS_VENDORING

## Quelle
- Upstream-Repository: https://github.com/cloudflare/skills.git
- Übernahmedatum: 2026-04-28
- Upstream Commit SHA: `7c449def4e0c63daa27212d853094e4c8e37bbe8`

## Übernommene Skill-Ordner
Die folgenden Verzeichnisse wurden selektiv aus `skills/` übernommen und als vendored Referenz unter `.agents/skills/cloudflare/` abgelegt:
- `agents-sdk`
- `cloudflare`
- `durable-objects`
- `sandbox-sdk`
- `web-perf`
- `workers-best-practices`
- `wrangler`
- `cloudflare-email-service`

## Zweck der vendored Dateien
- Diese Dateien sind **Referenz-/Agent-Skills** für Architektur, Agenten-Workflows und optionale Integrationen.
- Diese Dateien sind **kein direkt ausführbarer produktiver App-Code** des bestehenden Flask-Systems.
- Das bestehende Auto-Leads-System wurde dadurch nicht ersetzt oder neu aufgebaut.

## Lizenz & Attribution
- Lizenz-/Attribution-Dateien aus dem Upstream wurden übernommen:
  - `.agents/skills/cloudflare/LICENSE.cloudflare-skills`
- Nutzung erfolgt als interne Referenzbasis für Entwicklungs- und Integrationsrichtlinien.

## Update-Anleitung
1. In einem temporären Verzeichnis das Upstream-Repo klonen (oder fetchen) und Ziel-Commit ermitteln.
2. Nur die freigegebenen Skill-Ordner selektiv aus `skills/` synchronisieren:
   - `agents-sdk`, `cloudflare`, `durable-objects`, `sandbox-sdk`, `web-perf`, `workers-best-practices`, `wrangler`, `cloudflare-email-service`
3. Zielpfad im Auto-Leads-Repo: `.agents/skills/cloudflare/<skill-name>/` (Struktur beibehalten).
4. Lizenz-/Notice-Dateien erneut prüfen und bei Bedarf aktualisieren.
5. `docs/SKILLS_VENDORING.md` aktualisieren (Datum, SHA, ggf. geänderte Skill-Liste).
6. `docs/SKILLS_INTEGRATION_PLAN.md` auf neue/angepasste Empfehlungen abgleichen.
7. Validierung: Keine Secrets, keine aktive Produktivkopplung, lokale App-Startfähigkeit unverändert.
