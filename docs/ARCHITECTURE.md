# Architektur

**Last verified against commit:** `e7dc57e`

## Überblick
Auto-Leads ist als Flask-Monolith mit klarer Schichtung aufgebaut:

1. **Presentation Layer**: HTML-Views, Dashboard, API-Endpunkte
2. **Application Layer**: Route-Handler, Orchestrierung von Jobs
3. **Domain/Service Layer**: Suche, Audit, Extraktion, Scoring, Deduplizierung
4. **Persistence Layer**: SQLAlchemy-Modelle + Alembic-Migrationen (SQLite default)

## Komponenten
- **App Factory**: `app.create_app()` initialisiert Config, Extensions, Blueprints.
- **Zielstruktur (Runtime)**: `app/` ist das einzige Runtime-Package.
- **Blueprints**:
  - `app/routes/*` für Dashboard/Leads/Jobs/Export/API
  - `app/routes/web_compat.py` als temporäre, **deprecated** Legacy-URL-Schicht
- **Shared Layer**: `app/extensions.py`, `app/forms.py`, `app/utils.py`
- **Compatibility Layer**: `auto_leads/*` enthält nur Re-Exports und ist als deprecated markiert.
- **Services (`app/services/`)**:
  - Suche (`search_runner_service`, `google_places_service`)
  - Datenqualität (`duplicate_service`, `lead_score_service`)
  - Audit/Extraktion (`website_audit_service`, `extraction_service`, `seo_check_service`)
  - Export (`export_service`)

## Datenfluss (vereinfacht)
1. Nutzer startet Suchjob (Keyword + Städte + Zielanzahl).
2. Search-Runner ruft Google Places ab (paginiert, quota-sensitiv).
3. Rohkandidaten werden normalisiert und dedupliziert.
4. Website-Audit lädt Zielseiten kontrolliert (Timeout/SSRF-Schutz).
5. Extraktion + SEO-Checks reichern Lead-Datensatz an.
6. Scoring vergibt Punkte und Begründungen.
7. Persistenz in DB; Dashboard/API zeigen Fortschritt und Resultate.
8. Exportservice liefert CSV für CRM/Weiterverarbeitung.

## Schichtenregeln
- Routen enthalten keine schwere Fachlogik; diese gehört in Services.
- Services sollen idempotent und testbar sein.
- Datenzugriff über SQLAlchemy-Modelle; Schemaänderungen nur per Migration.
- Konfiguration ausschließlich aus `config.py` + Umgebungsvariablen.

## Querschnittsaspekte
- **Security**: CSRF, Rate-Limiter, SSRF-Schutz, Secret-Trennung.
- **Observability**: strukturiertes Logging pro Job/Lead.
- **Compliance**: DSGVO-Minimierung, robots/ToS-konformes Crawling.

## Codex-Subagent-Layer
- Projektbezogene Subagents liegen in `.codex/agents/`.
- Rollenbasierte Delegation ergänzt die Entwicklungsarchitektur um einen **AI-Execution-Layer**:
  - **Planung/Orchestrierung** (`planner`, `orchestrator`)
  - **Implementierung** (`backend-developer`, `fullstack-developer`, `frontend-developer`)
  - **Qualität/Sicherheit** (`reviewer`, `security-auditor`, `test-engineer`, `ci-cd-specialist`)
- Governance:
  - Security/Review standardmäßig read-only.
  - Keine parallelen Schreibzugriffe auf dieselben Dateien.
  - Große Features starten mit ExecPlan-Update gemäß `.agent/PLANS.md`.
- Referenzen:
  - `docs/SUBAGENTS.md` (Katalog + empfohlene Kernagenten)
  - `docs/SUBAGENTS_AUDIT.md` (Sicherheitsprüfung + Restrisiken)
