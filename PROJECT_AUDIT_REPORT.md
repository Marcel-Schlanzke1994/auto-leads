# Projekt-Audit: Auto-Leads (Flask)

## 1) Executive Summary

Das Projekt ist eine solide Basis für lokale Lead-Qualifizierung (Erfassung, Scoring, Website-Audit, CSV-Import, API).
Der aktuelle Stand ist **funktionsfähig**, jedoch bestehen operative Risiken bei Skalierung und Automatisierung:

- Website-Audits konnten bisher interne/private Ziele erreichen (SSRF-Risiko).
- URL-Eingaben waren nicht normalisiert (Fehler bei Audits durch uneinheitliche Formate).
- Wiederholte Logik für Default-Scoring erschwert Wartung.
- Für eine vollständige Lead-Automation fehlen Integrationen (CRM, Outreach-Sequenzen, Terminbuchung, Event-Tracking).

## 2) Durchgeführte Systemchecks

- Funktionale Tests (`pytest`) für Kernlogik und Endpunkte.
- Format-/Style-Check (`black --check .`).
- Statischer Qualitätscheck (`flake8`).

Ergebnis: Basis ist stabil; keine Testfehler im aktuellen Umfang.

## 3) Bereits umgesetzte Optimierungen in diesem Audit

1. **Sicherheits-Guard für Website-Audits**
   - Blockiert Audits gegen lokale/private Hosts (z. B. `localhost`, private IP-Ranges, `.local`).
   - Reduziert SSRF-/Missbrauchsrisiken in produktiven Umgebungen.

2. **URL-Normalisierung vor Persistenz/Audit**
   - Standardisiert Eingaben auf HTTP/HTTPS mit sauberer Prüfung.
   - Verhindert unnötige Audit-Fehler durch unvollständige URL-Formate.

3. **Zentrale Default-Score-Logik**
   - Wiederholte Scoring-Pfade wurden in eine Helper-Funktion zentralisiert.
   - Erhöht Wartbarkeit und reduziert Inkonsistenzen.

## 4) Konkrete Empfehlungen (Priorisiert)

## P0 – Sofort (Sicherheit & Stabilität)

1. **CSRF-Schutz aktivieren** (Flask-WTF oder CSRF-Token Middleware).
2. **Rate-Limits für Audit/Import-Endpunkte** (z. B. Flask-Limiter).
3. **Transaktions- und Fehler-Monitoring** (Sentry, OpenTelemetry).
4. **Secrets-Härtung**: nur `.env`/Secret-Manager, niemals Klartext-Tokens im Code.

## P1 – Nächste Iteration (Automatisierung)

1. **CRM-Sync** (HubSpot/Pipedrive/Salesforce) mit bidirektionalem Statusmapping.
2. **Lead-Lifecycle-Automation**:
   - Trigger: Score > X → Outreach starten.
   - Trigger: keine Antwort nach N Tagen → Follow-up.
3. **Asynchrone Audits** (Celery/RQ + Redis), damit Import und UI nicht blockieren.
4. **Deduplication-Logik** über Domain + Company Name + Email.

## P2 – Skalierung (Performance & Vertriebseffekt)

1. **Priorisierungsmodell v2**: gewichtetes Modell + Conversion-Feedback-Loop.
2. **A/B-Testing der E-Mail-Templates** (Betreff, CTA, Value Proposition).
3. **Segment-basierte Pipelines** (Branche, Stadt, Score-Buckets).
4. **Dashboard-KPIs**:
   - MQL→SQL Quote
   - Antwortquote je Segment
   - Time-to-First-Contact
   - Won-Rate nach Scoreklasse

## 5) Tool-/Stack-Empfehlungen

- **Orchestrierung/Automatisierung**: n8n oder Make.com (schneller MVP), später ggf. Temporal/Celery.
- **CRM**: HubSpot (schneller Einstieg) oder Pipedrive (einfaches Sales-Team-Fit).
- **E-Mail-Sequenzen**: Lemlist, Instantly, oder CRM-native Sequencer.
- **Datenqualität**: ZeroBounce / NeverBounce + eigene Domain-Validierung.
- **Observability**: Sentry + strukturierte Logs (JSON) + Uptime Checks.

## 6) Umsetzungsplan (30 Tage)

- **Woche 1**: Security/Guardrails, CSRF, Logging, Rate-Limits.
- **Woche 2**: CRM-Integration + Status-Mapping + dedizierte Webhooks.
- **Woche 3**: Async-Audits + Queueing + Retry-Strategien.
- **Woche 4**: KPI-Dashboard + Outreach-A/B-Tests + Review der Conversion-Kette.

## 7) Hinweise zu zusätzlichen Governance-Anforderungen

Im bereitgestellten Repository sind aktuell **keine** Module für Calendar-API, Discord-Cogs oder Mongo-Event-Schemas enthalten. Die genannten Prüfpflichten (Token-Speicherung, Calendar-Tokens, Mongo-Event-Format, Discord-Loop-Schutz) sind deshalb als **Backlog-Kriterien** für zukünftige Integrationen zu behandeln.

