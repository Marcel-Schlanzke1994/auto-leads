# SECURITY_EVIDENCE (Standard vor PR)

_Stand: 2026-04-28_

Dieses Dokument definiert verpflichtende Security-Nachweise vor PR-Erstellung bei relevanten Änderungen.

## 1) Secret-Pattern-Scan

**Ziel:** Verhindern, dass Secrets versehentlich committet werden.

**Mindestnachweis:**
- Suchlauf über typische Secret-Muster.
- Ergebnis mit Trefferliste (oder `no findings`) dokumentieren.

**Beispielkommando:**
```bash
rg -n --hidden --glob '!.git' '(AKIA[0-9A-Z]{16}|AIza[0-9A-Za-z\-_]{35}|ghp_[0-9A-Za-z]{36}|xox[baprs]-[0-9A-Za-z-]{10,}|-----BEGIN (RSA|EC|OPENSSH) PRIVATE KEY-----|(?i)api[_-]?key\s*[:=]\s*["\x27]?[A-Za-z0-9_\-]{16,})' .
```

## 2) Suche nach API-Keys/Tokens (projektweit)

**Ziel:** Sicherstellen, dass nur `.env`/Secret-Store genutzt wird.

**Mindestnachweis:**
- Treffer aus Konfigurations- und Quellcodepfaden prüfen.
- False Positives markieren und begründen.

**Beispielkommando:**
```bash
rg -n --hidden --glob '!.git' '(token|secret|apikey|api_key|access_key|client_secret|bearer)' app auto_leads docs .agent .agents
```

## 3) Prüfung auf `danger-full-access`

**Ziel:** Verhindern, dass riskante Ausführungsmodi unbemerkt in Artefakten verbleiben.

**Mindestnachweis:**
- Trefferliste inkl. Kontext und Begründung (falls absichtlich in Doku erwähnt).

**Beispielkommando:**
```bash
rg -n 'danger-full-access' .
```

## 4) Prüfung auf destruktive Commands

**Ziel:** Erkennen riskanter Befehle vor Merge.

**Mindestnachweis:**
- Suche nach typischen destruktiven Kommandos.
- Jeder Treffer muss als verboten, entschärft oder explizit dokumentiert bewertet werden.

**Beispielkommando:**
```bash
rg -n --hidden --glob '!.git' '(rm\s+-rf|git\s+reset\s+--hard|git\s+clean\s+-fd|drop\s+table|truncate\s+table|delete\s+from\s+[^\n]+\s+where\s+1\s*=\s*1)' .
```

## 5) Runtime-Verifikations-Template für externe APIs

Für jede neue/geänderte externe API ist folgende Struktur zu dokumentieren:

- API/Endpoint:
- Authentisierungsmethode (ohne Secret-Werte):
- Timeout/Retry/Backoff-Konfiguration:
- Erfolgsfall lokal verifiziert am:
- Fehlerfälle lokal verifiziert (4xx/5xx/Timeout):
- Nicht lokal verifizierbar (mit Grund):
- Geplanter Runtime-Check (Monitoring/Alerting):
- Residual Risk:

## 6) Compliance-Marker für Crawling/Lead-Workflows

Vor PR müssen folgende Marker pro relevantem Workflow gesetzt werden (`yes/no` + Evidenz):

- `robots geprüft`
- `ToS geprüft`
- `Rate-Limit definiert`
- `personenbezogene Daten minimiert`
- `Speicherzweck dokumentiert`

## Evidence-Format im PR (Mindeststandard)

- Ausgeführte Kommandos inkl. Exit-Status
- Relevante Auszüge/Dateipfade
- Interpretation der Ergebnisse (inkl. False Positives)
- Offene Risiken + Mitigation + Residual Risk
