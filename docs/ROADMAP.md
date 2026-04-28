# Roadmap

## v1 – Stabiler Core (kurzfristig)
- Konsistente Lead-Pipeline (Search → Dedupe → Audit → Score → Export)
- Robuste Fehlerbehandlung bei Google-Quota/Timeouts
- Basis-Dashboard für Jobstatus und Qualitätskennzahlen
- CI mit pytest/black/flake8 als Pflichtcheck

### Risiken
- Externe API-Limits
- unvorhersehbare Website-Strukturen bei Extraktion

### Abhängigkeiten
- Google Places API Key + aktivierte Billing/Quota
- stabile Netzwerkverbindung für externe Audits

## v2 – Produktqualität & Effizienz (mittelfristig)
- Verbesserte Scoring-Erklärbarkeit (Score-Breakdown)
- Bessere Kontakt-/Impressumserkennung
- Retry-/Backoff-Strategien je externem Provider
- Monitoring für Jobdauer, Fehlerraten, Exportqualität

### Risiken
- steigende Laufzeiten pro Job
- höhere Komplexität in Heuristiken

### Abhängigkeiten
- Testdatenkorpus für Extraktionsqualität
- Baseline-Metriken aus v1

## v3 – Operative Reife & Skalierung (langfristig)
- Optional asynchrone Worker-Architektur für große Jobs
- Mandanten-/Teamfähigkeit (Rollen, Audit-Logs)
- Erweiterte Compliance-Controls (Retention, Löschkonzepte)
- CI/CD mit automatisierten Security-Scans und Release-Gates

### Risiken
- Migrationsaufwand vom Monolith zu Worker-Modell
- Betriebs- und Wartungskosten

### Abhängigkeiten
- Architekturentscheidung zu Queue/Worker (z. B. Redis/Celery)
- klare SLA/SLI-Definition für Betrieb
