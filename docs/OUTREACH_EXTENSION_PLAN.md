# Outreach Extension Plan

## Ist-Struktur

### Entry Point
- `run.py` startet die Flask-App über `app.create_app()`.
- `app/__init__.py` lädt `.env`, initialisiert Extensions (`db`, `csrf`, `limiter`, `migrate`) und registriert Blueprints (`dashboard`, `leads`, `jobs`, `outreach`, `export`, `api`, `web_compat`).

### Models
- Kernmodell `Lead` in `app/models.py` inkl. Beziehungen zu Outreach-relevanten Modellen.
- Outreach/Compliance-Modelle in `app/models.py`:
  - `ContactAttempt`
  - `OutreachDraft`
  - `OptOut`
  - `Blacklist`
- Auditmodelle (`AuditResult`, `AuditIssue`) als Datenbasis für personalisierte Drafts.

### Blueprints
- `app/routes/leads.py`: Statuswechsel, Draft-Erstellung, ContactAttempts, Callback/Block-Handling.
- `app/routes/outreach.py`: Outreach-Übersicht (Drafts, Callback-Items, OptOut/Blacklist-Listen).
- `app/routes/export.py`: CSV-Export (gesamt, high-potential, gefiltert).

### Services
- `app/services/outreach_draft_service.py`: Block-Checks (OptOut/Blacklist), Draft-Generierung mit Audit-Personalisierung.
- `app/services/export_service.py`: CSV-Aufbereitung inkl. Outreach-Metadaten (`contact_status`, `outreach_allowed`, `draft_count`, `attempt_count`).
- `app/services/contact_form_service.py`: Draft-Erzeugung für Kontaktformulare (nur Draft, kein Versand).

### Templates
- `app/templates/lead_detail.html`: UI für Drafts, Status, ContactAttempts, Callback und Block-Management.
- `app/templates/outreach.html`: Übersicht zu heißen Leads, Drafts, Rückrufen und Compliance-Einträgen.

### Tests
- Bestehende Integrationstests in `tests/test_app.py` (u. a. CSV/Outreach-Basisfälle).
- Erweiterte Tests in `tests/test_outreach_extension.py` für zusätzliche Outreach- und Compliance-Regressionen.

### Config
- Zentrale Konfiguration in `config.py` ausschließlich über Umgebungsvariablen.
- Relevante Schalter: `REQUEST_TIMEOUT`, `PLACES_PROVIDER`, API-Token/Rate-Limit-Konfiguration.

## Neue/geänderte Dateien

### Neu
- `docs/OUTREACH_EXTENSION_PLAN.md`
- `tests/test_outreach_extension.py`

### Geändert
- Keine produktiven Python-Dateien geändert.

## DB-Änderungen/Migrationen
- Für diese Erweiterung wurden **keine neuen DB-Tabellen/-Spalten** eingeführt.
- Bestehende Outreach-Modelle sind bereits per Migration vorhanden (siehe `migrations/versions/b1f4d7c9e2aa_add_outreach_and_compliance_models.py`).
- Daher ist **keine zusätzliche Alembic-Migration** erforderlich.

## Start-/Testbefehle

### Start
```bash
python run.py
```

### Tests & Lint
```bash
pytest
black --check .
flake8
```

## Compliance-Hinweis
- Outreach-Funktionalität ist auf **Draft-Erstellung und manuelle Freigabe** ausgelegt.
- Es findet **keine automatische Massenwerbung** und kein automatischer Bulk-Versand statt.
- Contact-Form-Drafts werden explizit als `auto_send: false` gespeichert und müssen manuell geprüft werden.
