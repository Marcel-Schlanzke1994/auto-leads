# MULTI_AGENT_GATE (verbindlich)

_Stand: 2026-04-28_

Dieses Dokument definiert das formale Merge-Gate für risikorelevante Änderungen in `auto-leads`.

## Geltungsbereich

Das Gate ist verpflichtend für Änderungen mit Bezug zu:
- Security/Auth/Session
- API-Verträgen und externen Integrationen
- Crawling/Scraping/Web-Extraction
- Datenmodell/Migration
- CI/CD
- Export/Reporting mit Compliance- oder PII-Relevanz

## Reihenfolge (fix)

1. `planner`
2. `reviewer`
3. `security-auditor`
4. `owner-agent` (Integrations- und Entscheidungsinstanz)

Ein späteres Gate darf erst starten, wenn das vorherige Gate dokumentierte Outputs geliefert hat.

## Gate-Inputs

### planner
- Task-Beschreibung inkl. Scope
- Betroffene Dateien/Komponenten
- ExecPlan-Status und Triggercheck (`.agent/PLANS.md`)

### reviewer
- Plan-Artefakte vom planner
- Code-/Dokudiff
- Test-/Lint-Ergebnisse (oder Doku-only-Begründung)

### security-auditor
- Review-Ergebnis inkl. offener Risiken
- Security-Evidence (`docs/SECURITY_EVIDENCE.md`)
- Externe API-/Crawler-Verifikation

### owner-agent
- Konsolidierte Findings aus reviewer + security-auditor
- Nachweise zu Fixes oder bewusst akzeptierten Restrisiken
- Gate-Status aller Pflichtchecks

## Gate-Outputs

### planner Output
- Scope, Risiken, Abhängigkeiten
- ExecPlan-Pflichtentscheidung mit Triggerreferenz

### reviewer Output
- Qualitätsbewertung
- Findings im standardisierten Schema (mindestens severity/confidence/impact/mitigation/evidence)
- Merge-Empfehlung oder Blocker

### security-auditor Output
- Security-/Compliance-Bewertung
- Findings im vollständigen Schema
- Stop-the-line-Markierung bei `critical` ohne Mitigation

### owner-agent Output
- Merge-/No-Merge-Entscheidung
- Konfliktauflösung
- Residual-Risk-Dokumentation
- Follow-up-Aktionen mit Verantwortlichkeit

## Exit-Kriterien

Merge ist nur zulässig, wenn alle Punkte erfüllt sind:

1. Alle Pflicht-Gates wurden in Reihenfolge durchlaufen.
2. Pflicht-Evidence ist vollständig und nachvollziehbar.
3. Keine offenen `critical`-Findings ohne dokumentierte Ausnahmeentscheidung.
4. Residual Risk ist explizit dokumentiert.
5. ExecPlan wurde bei Trigger-Fällen aktualisiert.

## Konfliktlösung

Bei Widersprüchen zwischen reviewer und security-auditor gilt:

1. Faktenabgleich auf Evidence-Ebene.
2. Falls ungelöst: owner-agent priorisiert Sicherheitsrisiko vor Liefergeschwindigkeit.
3. Bei weiterhin unklarer Lage: `No-Merge` + Follow-up-Task mit klarer Prüfstrategie.

## Merge-/No-Merge-Entscheidung

### Merge
- Alle Exit-Kriterien erfüllt.
- Restrisiko ist akzeptiert, dokumentiert und terminiert.

### No-Merge
- Fehlende Evidence, offene High/Critical-Risiken oder unvollständiger Plan/Gate-Ablauf.

## Residual-Risk-Dokumentation (Pflichtfelder)

- Risiko-Beschreibung
- Betroffene Assets/Dateien
- Severity + Confidence
- Akzeptanzbegründung (warum kein Blocker)
- Temporäre Mitigation
- Fälligkeit für dauerhafte Behebung
- Verantwortliche Rolle
