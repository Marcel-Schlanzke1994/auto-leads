# SKILLS REVIEW – neue Skill-Integration

_Stand: 2026-04-28_

## Kontext & Vorgehen

Diese Review wurde mit drei Subagent-Perspektiven durchgeführt:

- **planner**: prüft Planbarkeit, Governance und Anschluss an `.agent/PLANS.md`.
- **reviewer**: prüft Qualität, Konsistenz, Testbarkeit und Integrationsrisiken.
- **security-auditor**: prüft Security/Compliance-Risiken (Secrets, ToS/robots, Datenschutz, externe Requests).

Scope der Prüfung:

- `.agents/skills/*/SKILL.md`
- `docs/SKILLS.md`
- `docs/SKILLS_AUDIT.md`
- `docs/SUBAGENTS.md`
- `.agent/PLANS.md`

---

## Findings

### 1) Reviewer-Findings (Qualität & Integrationskonsistenz)

1. **Stark positiv: einheitliches Skill-Grundmuster ist vorhanden.**
   Fast alle Skills nutzen konsistente Abschnitte (`Purpose`, `When to use`, `Workflow`, `Safety Guardrails`, `Output`). Das erleichtert Onboarding und reduziert Interpretationsspielräume.

2. **Lücke: fehlende "Definition of Done" pro Skill.**
   Die meisten Skills enden mit einer generischen Output-Formel, aber ohne konkrete Abnahmekriterien (z. B. verpflichtende Artefakte, Nachweise, Dateipfade). Dadurch steigt das Risiko uneinheitlicher Ausführung.

3. **Lücke: schwache Verknüpfung zwischen Skills und projektweiten Quality Gates.**
   In den Skill-Dateien fehlt i. d. R. der explizite Hinweis auf projektweite Checks (`pytest`, `black --check .`, `flake8`) für Code-Änderungen. Das kann bei delegierten Ausführungen zu Auslassungen führen.

4. **Lücke: fehlende Skill-Auswahlmatrix für typische Aufgabenklassen.**
   `docs/SKILLS.md` listet Skills gut, aber es fehlt ein verbindlicher Entscheidungsbaum ("welcher Skill-Kombinationssatz bei welchem Task"). Dadurch droht entweder Over-Delegation oder Skill-Auswahl nach Bauchgefühl.

### 2) Security-Auditor-Findings (Security & Compliance)

1. **Stark positiv: Security-Guardrails sind in kritischen Skills enthalten.**
   Besonders in `security-review`, `website-audit`, `web-extraction`, `auto-lead-discovery` werden zentrale Controls (Secrets via Env, ToS/robots/DSGVO, Rate-Limits) adressiert.

2. **Lücke: fehlende explizite Verifikationsschritte für Secret-Leaks.**
   Es gibt Verbote ("keine Secrets"), aber keine standardisierten Prüfkommandos oder Nachweispflicht vor PR (z. B. pattern scan). Das reduziert Auditierbarkeit.

3. **Lücke: keine standardisierte Risiko-Klassifizierung in Skill-Outputs.**
   Outputs fordern Zusammenfassungen, aber nicht konsistent `severity`, `confidence`, `exploit prerequisites` (für Security-Fälle). Das erschwert Priorisierung in Incident-/Review-Situationen.

4. **Lücke: externe API-/Crawler-Änderungen ohne verpflichtendes Runtime-Verification-Template.**
   Statische Guardrails sind vorhanden; jedoch fehlt ein verpflichtendes Template, was lokal validiert wurde vs. was nur in Runtime/Prod verifiziert werden kann.

### 3) Planner-Findings (Planung & Governance)

1. **Positiv: Subagent- und Skill-Kataloge sind umfassend dokumentiert.**
   Das schafft Transparenz über verfügbare Rollen und Sicherheitslevel.

2. **Lücke: "große Features" ist als Trigger für ExecPlan zu unscharf.**
   Es fehlt eine objektive Schwelle (z. B. "mehr als 3 Dateien", "Schemaänderung", "externe API-Flows"). Das führt zu inkonsistenter Planpflicht.

3. **Lücke: fehlende direkte Mapping-Tabelle Skill → PLANS/ExecPlan-Artefakte.**
   Planpflicht ist beschrieben, aber ohne Skill-spezifische Soll-Artefakte (z. B. bei `database-design`: Risiko- und Rollback-Abschnitt verpflichtend).

4. **Lücke: kein operativer Integrations-Checkpoint zwischen planner/reviewer/security-auditor.**
   Es fehlt ein standardisiertes Merge-Gate (Reihenfolge, Inputs/Outputs, Exit-Kriterien), obwohl die Rollen klar vorhanden sind.

---

## Risiken (priorisiert)

### Hoch

1. **Uneinheitliche Qualität bei delegierter Skill-Ausführung**
   - Treiber: fehlende DoD + fehlende harte Quality-Gate-Verankerung in Skill-Dateien.
   - Effekt: unvollständige Reviews, Lücken bei Tests/Lint, variable Ergebnisqualität.

2. **Security-Review nicht ausreichend nachweisbar/auditierbar**
   - Treiber: keine verpflichtenden Leak-/Verification-Nachweise im Skill-Output.
   - Effekt: höhere Residual-Risiken vor Merge, schwierige forensische Nachvollziehbarkeit.

### Mittel

3. **Planpflicht bei größeren Änderungen wird inkonsistent angewendet**
   - Treiber: fehlende objektive Trigger + fehlendes Skill→ExecPlan-Mapping.
   - Effekt: Architektur-/Risikoentscheidungen werden nicht reproduzierbar dokumentiert.

4. **Konfliktrisiko bei paralleler Multi-Agent-Nutzung**
   - Treiber: kein fixer Integrations-Checkpoint (Inputs/Outputs/Reihenfolge).
   - Effekt: doppelte Arbeit, widersprüchliche Empfehlungen, unklare Priorisierung.

---

## Konflikte / Spannungsfelder

1. **Selektive Skill-Nutzung vs. breite Verfügbarkeit**
   - Die Policy fordert selektives Laden, während sehr viele Skills/Subagents verfügbar sind.
   - Ohne Auswahlmatrix entsteht ein Spannungsfeld zwischen "kontextarm" und "alles ist verfügbar".

2. **Read-only Audit-Rollen vs. operative Nachweisanforderungen**
   - Reviewer/Security-Auditor sind read-only gedacht; Nachweise (Tests/Scans) müssen dennoch in den Workflow eingebunden werden.
   - Es fehlt eine klare Regel, wer die Evidence erzeugt und wer sie formal abnimmt.

3. **Dokumentierte Guardrails vs. fehlende Gate-Mechanik**
   - Viele Guardrails sind textlich vorhanden.
   - Ohne verpflichtende Checklisten/DoD/Gates bleibt die Durchsetzung teilweise freiwillig.

---

## Konkrete Verbesserungen (umsetzbar)

### Quick Wins (1–2 Tage)

1. **Skill-Template erweitern um verpflichtende Abschnitte**
   - `Definition of Done`
   - `Required Evidence` (Kommandos + Artefakte)
   - `Out-of-scope`

2. **Einheitliches Output-Schema für Review/Security-Skills**
   - Felder: `severity`, `confidence`, `impact`, `prerequisites`, `mitigation`, `residual risk`.

3. **`docs/SKILLS.md` um Skill-Auswahlmatrix ergänzen**
   - Beispiel: API-Änderung ⇒ `backend-api` + `security-review` + `test-generation` + `code-review`.

### Mittelfristig (3–7 Tage)

4. **Verbindliches Multi-Agent-Gate definieren (planner → reviewer → security-auditor)**
   - Inputs, Outputs, Exit-Kriterien pro Gate.
   - Expliziter Konfliktlösungsmechanismus (wer entscheidet bei Widerspruch).

5. **Objektive ExecPlan-Trigger ergänzen**
   - Z. B. externe APIs/Crawling, Datenmodelländerung, migrationspflichtige Änderungen, neue Exportpfade.

6. **Nachweisbare Security-Evidence vor PR standardisieren**
   - Minimal: Secret-Pattern-Scan + dokumentierte Runtime-Verifikation für externe Integrationen.

### Governance (kontinuierlich)

7. **Quartalsweiser Skills/Subagents Drift-Check**
   - Prüfen auf veraltete Anweisungen, redundante Skills, fehlende Guardrails.

8. **Skill-spezifische Compliance-Marker für Lead/Scraping-Workflows**
   - Robots/ToS/DSGVO-Status je Task explizit im Output ausweisen.

---

## Vorschlag für standardisierten Review-Ablauf

1. **planner**
   - Scope + Risiken + Abhängigkeiten definieren
   - Entscheidung, ob ExecPlan-Update erforderlich ist

2. **reviewer**
   - Korrektheit, Regressionen, Testabdeckung, Integrationsgrenzen prüfen
   - Findings nach Severity + Confidence liefern

3. **security-auditor**
   - Threat-Pfade, Secrets, Input-Handling, externe Requests/Compliance prüfen
   - Containment-Optionen für High Severity ergänzen

4. **Integration Gate (Owner-Agent)**
   - Konflikte auflösen
   - Rest-Risiko + Follow-ups explizit dokumentieren
   - Merge-/No-Merge-Entscheidung begründen

---

## Fazit

Die Skill-Integration ist bereits strukturiert und grundsätzlich sicherheitsbewusst. Die größten Hebel liegen nicht in neuen Regeln, sondern in **verbindlicher Durchsetzung**: klare DoD, einheitliche Evidence, objektive Plan-Trigger und ein formales Multi-Agent-Integrations-Gate.
