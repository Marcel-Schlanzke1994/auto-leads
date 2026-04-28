# code-review

## Purpose
Strukturiertes Review für Python/Flask, API- und Datenflussqualität.

## When to use
- Vor Merge jeder produktiven Änderung.
- Bei Refactorings oder Schnittstellenänderungen.

## Workflow
1. Änderung gegen Anforderungen und ExecPlan spiegeln.
2. Prüfen: Lesbarkeit, Fehlerpfade, Abwärtskompatibilität, Tests.
3. Spezifisch für auto-leads: Service-Layer in `app/services/` beibehalten.
4. Review-Output: Findings nach Severity (high/medium/low).

## Safety Guardrails
- Keine pauschalen Approvals ohne reproduzierbare Begründung.
- Security- und Datenschutzaspekte immer separat ausweisen.

## Output
- Kurze Zusammenfassung, getroffene Annahmen, Risiken und nächste Schritte.
