# Skills Security Audit (2026-04-28)

## Scope
- Quelle: `https://github.com/VoltAgent/awesome-agent-skills` (kuratiertes Verzeichnis, kein direkter Skill-Quellbaum im Repo).
- Übernahmeziel: projektrelevante Skills für `auto-leads` unter `.agents/skills/`.
- Fokus: Sicherheit, Compliance, Kontextökonomie.

## Übernommene Skills

### Aus Awesome-Ökosystem übernommen (konzeptionell adaptiert)
- `commit`, `code-review`, `security-review`, `debug`, `test-generation`, `ci-failure-resolution`
- `documentation`, `api-documentation`, `database-design`, `backend-api`, `frontend-ui`
- `website-audit`, `lead-generation`, `web-extraction`, `report-generation`, `data-cleaning`, `export-csv-excel`, `dashboard-design`

### Neu für auto-leads erstellt
- `auto-lead-discovery`
- `impressum-extraction`
- `local-seo-audit`
- `lead-scoring`
- `lead-export`
- `client-report-generation`

## Nicht übernommen / deaktiviert

| Kategorie | Entscheidung | Risiko | Begründung |
|---|---|---|---|
| Cloud-/Provider-spezifische Skills (z. B. Terraform, Cloudflare, Stripe) | Nicht übernommen | niedrig | Projektfremd für aktuellen Flask-Lead-Stack. |
| Growth-/Marketing-Spam-nahe Workflows | Nicht übernommen | hoch | Risiko für ToS/Compliance/Brand-Schäden. |
| Skills mit möglicher Automations-Übersteuerung (massive Autop-runbooks) | Nicht übernommen | mittel | Gefahr von Kontextüberladung und Fehlsteuerung. |
| Unklare externe Netzwerk-Workflows ohne Guardrails | Nicht übernommen | hoch | Kein klarer Scope für DSGVO/Robots/Fair-Use. |

## Sicherheitsbewertung (übernommene Skills)

| Skillgruppe | Risiko-Level | Ergebnis |
|---|---|---|
| Review/Security/Test/CI | Niedrig–Mittel | Guardrails vorhanden; keine destruktiven Git-Defaults. |
| Web-Extraction/Lead-Discovery | Mittel–Hoch | Durch DSGVO-, robots.txt-, ToS-, Rate-Limit-Gates entschärft. |
| Export/Reporting | Mittel | Feld-Whitelisting und Datensparsamkeit vorgesehen. |

## Durchgeführte Entschärfungen
1. Keine hardcodierten Secrets; API-Keys nur via Umgebungsvariablen.
2. Explizite Verbote für destruktive Git-Befehle als Default.
3. Klare Regeln gegen aggressive Scraping-/Bot-Evasion-Techniken.
4. Netzwerkzugriffe in Skills nur mit Zweckbindung und Compliance-Hinweis.
5. Kontextüberladung reduziert durch lokale, task-fokussierte Skill-Selektion.

## Offene Restrisiken
- Website-Strukturen variieren stark; Kontakt-/Impressum-Heuristiken können False Positives erzeugen.
- Externe API-ToS können sich ändern und müssen regelmäßig nachgepflegt werden.
- Bei späterer Skill-Erweiterung ist erneutes Security-Review erforderlich.

## Empfehlung
- Quartalsweise Audit von `.agents/skills/` inklusive Pattern-Scan auf Secrets/destruktive Befehle.
- Bei neuen Scraping-Features vor Aktivierung ein separates Compliance-Review durchführen.
