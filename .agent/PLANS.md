# Verbindliches Planformat (`.agent/PLANS.md`)

Diese Datei definiert das **verbindliche Arbeitsformat** für Planung, Steuerung und Status-Tracking im Repository `auto-leads`.

## Operativer Master-Plan
Alle Maßnahmen in diesem Dokument sind auf den operativen Master-Plan auszurichten:
- `docs/execplans/auto-lead-system-execplan.md`

Bei Widersprüchen gilt: **ExecPlan > lokale Task-Notizen**. Task-Notizen dürfen den ExecPlan präzisieren, aber nicht konterkarieren.

---

## Pflichtstruktur für jeden Plan
Jeder neue Plan-Eintrag (Feature, Epic, Refactor, Incident-Fix) MUSS die folgenden Abschnitte enthalten:

1. **Ziele**
2. **Milestones**
3. **Decision Log**
4. **Risks**
5. **Progress**

Fehlende Abschnitte gelten als unvollständiger Plan.

---

## 1) Ziele (Outcome-orientiert)
Beschreibt den messbaren Zweck, nicht nur Aktivitäten.

**Mindestfelder:**
- `Problem`: Welches konkrete Problem wird gelöst?
- `Outcome`: Welcher fachliche/technische Nutzen wird erreicht?
- `KPIs`: Wie wird Erfolg messbar gemacht?
- `Non-Goals`: Was wird explizit **nicht** umgesetzt?

**Beispiel-Template:**
```md
## Ziele
- Problem: ...
- Outcome: ...
- KPIs:
  - ...
  - ...
- Non-Goals:
  - ...
```

---

## 2) Milestones (lieferbare Inkremente)
Teilt die Arbeit in überprüfbare, kleine Lieferpakete.

**Mindestfelder pro Milestone:**
- `Name`
- `Scope`
- `Dependencies`
- `Definition of Done`
- `Owner` (Team/Verantwortliche Rolle)
- `ETA` (Datum oder Sprint)

**Beispiel-Template:**
```md
## Milestones
### M1 – ...
- Scope: ...
- Dependencies: ...
- Definition of Done:
  - ...
- Owner: ...
- ETA: ...
```

---

## 3) Decision Log (nachvollziehbare Architektur-/Prozessentscheidungen)
Jede relevante Entscheidung wird dokumentiert, inklusive Trade-offs.

**Mindestfelder pro Entscheidung:**
- `Date`
- `Decision`
- `Rationale`
- `Alternatives considered`
- `Impact`

**Beispiel-Template:**
```md
## Decision Log
- Date: 2026-04-28
  - Decision: ...
  - Rationale: ...
  - Alternatives considered: ...
  - Impact: ...
```

---

## 4) Risks (technisch + operativ + compliance)
Risiken sind aktiv zu managen, nicht nur aufzulisten.

**Mindestfelder pro Risiko:**
- `Risk`
- `Type` (`technical`, `operational`, `security`, `compliance`)
- `Probability` (`low|medium|high`)
- `Impact` (`low|medium|high`)
- `Mitigation`
- `Trigger / Early warning`

**Beispiel-Template:**
```md
## Risks
- Risk: ...
  - Type: technical
  - Probability: medium
  - Impact: high
  - Mitigation: ...
  - Trigger / Early warning: ...
```

---

## 5) Progress (laufende Statusführung)
Progress wird fortlaufend aktualisiert, mindestens bei jedem Merge in den Branch.

**Mindestfelder:**
- `Status` (`planned|in_progress|blocked|done`)
- `Last update` (ISO-Datum)
- `Completed since last update`
- `Next actions`
- `Open blockers`

**Beispiel-Template:**
```md
## Progress
- Status: in_progress
- Last update: 2026-04-28
- Completed since last update:
  - ...
- Next actions:
  - ...
- Open blockers:
  - ...
```

---

## Governance-Regeln
- Security-/Compliance-kritische Änderungen (externe APIs, Crawling, Export) erfordern expliziten Risiko-Eintrag.
- Bei Architekturänderungen sind `docs/ARCHITECTURE.md` und der ExecPlan konsistent mitzupflegen.
- Planänderungen ohne Update von `Decision Log` und `Progress` sind nicht zulässig.
