# Architektur

## Überblick
Auto-Leads ist als Flask-Monolith mit klarer Schichtung aufgebaut:

1. **Presentation Layer**: HTML-Views, Dashboard, API-Endpunkte
2. **Application Layer**: Route-Handler, Orchestrierung von Jobs
3. **Domain/Service Layer**: Suche, Audit, Extraktion, Scoring, Deduplizierung
4. **Persistence Layer**: SQLAlchemy-Modelle + Alembic-Migrationen (SQLite default)

## Komponenten
- **App Factory**: `app.create_app()` initialisiert Config, Extensions, Blueprints.
- **Blueprints**:
  - `app/routes/*` für Dashboard/Leads/Jobs/Export
  - `auto_leads/routes/api.py` für API-Endpunkte
  - `auto_leads/routes/web.py` für zusätzliche Web-Routen
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
