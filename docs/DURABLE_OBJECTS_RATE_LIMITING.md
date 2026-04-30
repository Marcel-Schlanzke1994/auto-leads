# Durable Objects Rate-Limit-/State-Planung (Phase 3)

## Zweck im Auto-Leads-System

Durable Objects (DO) dienen hier als **optionale** Koordinationsschicht für konsistente Rate-Limits und einfachen verteilten Job-State. Ziel ist ein sicherer Prototyp für spätere Erweiterungen, ohne die bestehende lokale Flask-Architektur zu ersetzen.

## Warum optional

- Das lokale Flask-System bleibt führend und lauffähig ohne Cloudflare.
- Keine Cloudflare-Pflichtabhängigkeit zur Laufzeit.
- Lokale Entwicklung, Tests und bestehende Workflows dürfen nicht blockiert werden, wenn Worker/DO nicht verfügbar sind.

## Was NICHT ersetzt wird

Durable Objects ersetzen **nicht**:

- lokale SQLite-Datenbank und bestehende Modelle,
- Flask-Routen/Businesslogik,
- lokale Audit-/Outreach-Prozesse,
- bestehende Compliance-/Freigabelogik.

## Mögliche zukünftige Koordination über DO

- `OutreachRateLimitState`
- `AuditJobState`
- `EmailSendState`
- `LeadProcessingState`

In dieser Phase ist nur ein einfacher Rate-Limit-Prototyp implementiert.

## Rate-Limit-Konzept (Zielmodell)

Rate-Limits können später parallel auf mehreren Ebenen gelten:

- **pro Lead**: z. B. limitierte Aktionen je Lead-ID/Hash pro Zeitfenster
- **pro Domain**: z. B. limitierte Aktionen je Domain
- **pro Route/Operation**: z. B. unterschiedliche Limits für `draft`, `approve`, `send`
- **pro Tag**: z. B. Tagesobergrenze als zusätzliche Kappe
- **Burst + Sustained**:
  - Burst-Limit: kurzfristige Spitzen begrenzen
  - Sustained-Limit: langfristige Last innerhalb fairer Grenzen halten

## Failure Modes und Verhalten

1. **Durable Object nicht erreichbar**
   - Worker liefert Fehler oder Timeout.
   - Flask muss auf lokalen Default zurückfallen (kein Hard-Fail durch Cloudflare-Abhängigkeit).

2. **Cloudflare Worker deaktiviert**
   - Feature-Flag/ENV deaktiviert Worker-Zugriffe.
   - System läuft lokal weiter.

3. **Lokaler Flask-Fallback**
   - Entscheidung bleibt lokal möglich.
   - Keine blockierende externe Pflichtprüfung für lokale Entwicklung.

4. **Keine blockierende Abhängigkeit**
   - DO ist assistive Architektur, nicht Single Point of Failure für den lokalen Betrieb.

## Datenschutzvorgaben

- Keine vollständigen Lead-Daten im Durable Object speichern.
- Nur minimale IDs/Hashes/Zähler verwenden.
- Keine E-Mail-Inhalte speichern.
- Keine personenbezogenen Logs erzeugen.

## Spätere Integrationspunkte (optional)

Flask könnte zukünftig optional den Worker fragen, **bevor** Aktionen ausgeführt werden, z. B.:

- Outreach-Draft
- Freigabe
- Send

Dabei gilt:

- Worker/DO entscheidet nur über **Rate-Limit/State**.
- Businesslogik bleibt im Flask-System.

## Prototyp-Endpunkt (Phase 3)

`POST /rate-limit/check`

Request:

```json
{
  "scope": "lead|domain|operation",
  "key": "string",
  "limit": 10,
  "windowSeconds": 60
}
```

Response:

```json
{
  "allowed": true,
  "remaining": 9,
  "resetAt": "2026-04-28T12:00:00.000Z",
  "scope": "domain",
  "key": "example-hash"
}
```

Hinweis: `key` ist als Hash/ID zu verstehen; keine Klardaten erforderlich.
