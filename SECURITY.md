# Security Policy

## Supported Versions
Aktiv unterstützte Version ist jeweils der aktuelle `main`-Branch.

## Secret-Handling
- Secrets ausschließlich über Umgebungsvariablen (`.env`, CI-Secret-Store).
- Niemals API-Keys/Tokens in Quellcode, Tests, Fixtures oder Dokumente committen.
- Für lokale Entwicklung `.env.example` als Vorlage nutzen.
- Produktions-Deployments müssen dedizierte Secret-Stores (z. B. GitHub Secrets, Vault, Cloud Secret Manager) verwenden.

## Incident Response
1. **Erkennen**: Incident dokumentieren (Zeitpunkt, Scope, betroffene Systeme).
2. **Eindämmen**: kompromittierte Keys sofort deaktivieren/rotieren, schädliche Jobs stoppen.
3. **Beheben**: Root Cause Analysis, Hotfix, zusätzliche Schutzmaßnahmen.
4. **Wiederherstellen**: Dienste kontrolliert hochfahren, Logs und Fehlerraten überwachen.
5. **Nachbereitung**: Postmortem mit Maßnahmenliste und Verantwortlichkeiten.

## Rotation-Prozess (Keys/Tokens)
- Rotation bei Verdacht, Leak, Rollenwechsel und mindestens quartalsweise für hochprivilegierte Schlüssel.
- Reihenfolge:
  1. neuen Key erzeugen,
  2. Secret-Store aktualisieren,
  3. Deploy/Neustart,
  4. Smoke-Test,
  5. alten Key widerrufen.
- Rotation im Change-Log/Runbook dokumentieren.

## Responsible Disclosure
Bitte Sicherheitslücken **nicht öffentlich** melden.

- Kontaktkanal: Security-Team/Repository-Maintainer (privater Kanal).
- Inhalte: Reproduktionsschritte, Impact, betroffene Version/Commit, ggf. PoC.
- Best Effort SLA: Erstreaktion innerhalb von 3 Werktagen.

## Mindestanforderungen im Projekt
- CSRF-Schutz für Form-Aktionen.
- Rate-Limiting für API-Endpunkte.
- SSRF-Schutz beim Website-Fetching.
- Logging ohne Secret-Leaks.
