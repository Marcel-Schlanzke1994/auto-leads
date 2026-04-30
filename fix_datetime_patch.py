from pathlib import Path
import shutil
import sys

app = Path(r"C:\AutoLeads\auto-leads")
p = app / "app" / "services" / "lead_score_service.py"
q = app / "app" / "services" / "outreach_draft_service.py"

if not p.exists():
    print("FEHLER: lead_score_service.py nicht gefunden")
    sys.exit(1)

shutil.copy2(p, p.with_suffix(p.suffix + ".bak_datetime_fix"))
if q.exists():
    shutil.copy2(q, q.with_suffix(q.suffix + ".bak_datetime_fix"))

text = p.read_text(encoding="utf-8")

if "from datetime import UTC, datetime" not in text:
    text = text.replace("from dataclasses import dataclass\n", "from dataclasses import dataclass\nfrom datetime import UTC, datetime\n", 1)

lines = text.splitlines()
start = None
for i, line in enumerate(lines):
    if line.startswith("def _latest_web_perf"):
        start = i
        break

if start is None:
    if "def _as_aware_utc" in text:
        print("OK: lead_score_service.py war bereits gepatcht")
    else:
        print("FEHLER: _latest_web_perf nicht gefunden")
        sys.exit(1)
else:
    end = None
    for i in range(start + 1, len(lines)):
        if lines[i].startswith("def _subscore"):
            end = i
            break
    if end is None:
        print("FEHLER: _subscore nicht gefunden")
        sys.exit(1)

    replacement = [
        "def _as_aware_utc(value):",
        "    if value is None:",
        "        return datetime.min.replace(tzinfo=UTC)",
        "",
        "    if value.tzinfo is None:",
        "        return value.replace(tzinfo=UTC)",
        "",
        "    return value.astimezone(UTC)",
        "",
        "",
        "def _latest_web_perf(lead):",
        "    if not lead.audit_results:",
        "        return {}",
        "",
        "    latest = max(",
        "        lead.audit_results,",
        "        key=lambda item: _as_aware_utc(item.created_at),",
        "    )",
        "",
        "    if latest.raw_pagespeed_json and isinstance(latest.raw_pagespeed_json, dict):",
        "        return latest.raw_pagespeed_json.get(\"web_perf\") or {}",
        "",
        "    return {}",
        "",
    ]
    lines = lines[:start] + replacement + lines[end:]
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("OK: lead_score_service.py gepatcht")

if q.exists():
    outreach = q.read_text(encoding="utf-8")
    old = "Blacklist.expires_at ^> datetime.now(UTC)"
    new = "Blacklist.expires_at ^> datetime.now(UTC).replace(tzinfo=None)"
    outreach = outreach.replace(old.replace("^", ""), new.replace("^", ""))
    q.write_text(outreach, encoding="utf-8")
    print("OK: outreach_draft_service.py geprüft")

print("PATCH OK")
