# Outreach Extension Plan

## Ist-Struktur (Bestandsaufnahme vor Umsetzung)

### Entry Point
- `run.py` startet die Flask-App über `app.create_app()`.
- `app/__init__.py` lädt `.env`, initialisiert `db`, `csrf`, `limiter`, `migrate` und registriert Blueprints (`dashboard`, `leads`, `jobs`, `outreach`, `export`, `api`, `web_compat`).

### Models / Datenbank
- Kernmodell `Lead` inkl. Beziehungen zu Audit- und Outreach-Objekten in `app/models.py`.
- Bereits vorhandene Outreach-Modelle in `app/models.py`: `ContactAttempt`, `OutreachDraft`, `OptOut`, `Blacklist`.
- Bereits vorhandene Migrationen für Outreach/Compliance:
  - `b1f4d7c9e2aa_add_outreach_and_compliance_models.py`
  - `d4e8a9f1c2b7_add_notes_and_draft_personalization.py`
  - `e7b9c2d4f1a6_add_company_fields_to_opt_outs_and_blacklists.py`

### Routes / Blueprints
- `app/routes/leads.py`: Lead-Detail, Statuswechsel, Draft-Erzeugung, ContactAttempts, Callback, OptOut/Blacklist.
- `app/routes/outreach.py`: Outreach-Dashboard (`/outreach`) mit Filtern/Übersichten.
- `app/routes/export.py`: CSV-Export-Endpunkte.

### Templates
- `app/templates/lead_detail.html`: Kontaktstatus, Draft-UI, ContactAttempts, Callback, Block-Warnung.
- `app/templates/outreach.html`: Statusübersicht, Hot-Leads, Drafts zur Prüfung, Callback-Liste, OptOut/Blacklist.

### Services
- `app/services/outreach_draft_service.py`: Draft-Personalisierung + Block-Checks.
- `app/services/contact_form_service.py`: Kontaktformular-URL-Erkennung + Draft-Text (kein Auto-Submit).
- `app/services/export_service.py`: CSV-Aufbereitung inkl. Outreach-Feldern.

### Tests
- `tests/test_outreach_extension.py` deckt Kernanforderungen der Outreach-Erweiterung ab.
- Weitere Regressionstests in `tests/test_app.py` und Service-Tests.

### Config / .env
- Konfiguration zentral in `config.py`; Secrets über `.env`.
- `.env.example` enthält Platzhalter, keine produktiven Tokens.

## Umgesetzte Erweiterungen (additiv, kompatibel)

1. **Blacklist additiv erweitert**
   - Zusätzliche Felder `email` und `domain` am Modell `Blacklist` ergänzt.
   - Bestehendes `entry_type`/`value`-Schema bleibt vollständig erhalten (abwärtskompatibel).

2. **Block-Checks robust erweitert**
   - Draft-Blockierung und CSV-Block-Markierung berücksichtigen sowohl
     - vorhandene `entry_type/value_normalized`-Einträge als auch
     - neue direkte Felder `blacklists.email` und `blacklists.domain`.

3. **Lead-Detail Blocking-Workflow ergänzt**
   - Beim Setzen einer Blacklist über `/leads/<id>/contact-block` werden bei `entry_type=email/domain`
     zusätzlich die neuen Felder `email` bzw. `domain` gesetzt.

4. **Outreach-Dashboard Query-Warnungen bereinigt**
   - SQLAlchemy-Subquery-Nutzung auf `select(...)` umgestellt, um SAWarnings zu vermeiden.

## Neu hinzugefügte Dateien
- `migrations/versions/f2c1a6e9b4d8_add_blacklist_email_domain_columns.py`

## Geänderte Dateien
- `app/models.py`
- `app/routes/leads.py`
- `app/routes/outreach.py`
- `app/services/outreach_draft_service.py`
- `app/services/export_service.py`
- `docs/OUTREACH_EXTENSION_PLAN.md`
- `README.md`

## Datenbankänderungen
- **Neue additive Spalten in `blacklists`:**
  - `email` (`String(255)`, indexiert)
  - `domain` (`String(255)`, indexiert)
- Migration: `f2c1a6e9b4d8_add_blacklist_email_domain_columns.py`

## Start-/Testbefehle

### Start
```bash
python run.py
```

### Migration
```bash
flask db upgrade
```

### Tests & Lint
```bash
pytest
black --check .
flake8
```

## Rechtliche Schutzlogik (verbindlich)
- Outreach erzeugt **nur Entwürfe (Drafts)**.
- **Kein automatischer SMTP-Versand** und keine automatische Massenwerbung.
- Kontaktformular-Unterstützung ist vorbereitend (URL-Erkennung + Draft), nicht blindes Auto-Submit.
- OptOut/Blacklist blockiert die Draft-Erzeugung und wird im Lead-Detail klar als „Kontakt gesperrt“ angezeigt.
