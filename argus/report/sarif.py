"""SARIF 2.1.0 export: findings ingestible by GitHub code scanning,
Azure DevOps and most CI security dashboards. report.md/.html stay the
human artifacts; report.sarif is the machine contract."""
from __future__ import annotations

import json
import time
from pathlib import Path

from ..session import Session, _cwe_of, _owasp_of, sanitized_findings

_LEVEL = {"critical": "error", "high": "error", "medium": "warning",
          "low": "warning", "info": "note"}
_RANK = {"critical": 9.5, "high": 8.0, "medium": 5.5,
         "low": 3.0, "info": 1.0}


def render_sarif(session: Session) -> Path:
    sev_order = list(_LEVEL)
    findings = sorted(sanitized_findings(session.findings), key=lambda f:
                      sev_order.index(f.get("severity"))
                      if f.get("severity") in sev_order else len(sev_order))
    rules: dict[str, dict] = {}
    results = []
    for f in findings:
        cwe = f.get("cwe") or _cwe_of(f.get("category"))
        rule_id = cwe or str(f.get("category") or "finding").lower()
        rules.setdefault(rule_id, {
            "id": rule_id,
            "name": f.get("category", "finding"),
            "shortDescription": {"text": f.get("category", "")},
            "properties": {},
        })
        if cwe and "-" in cwe:
            _num = cwe.split("-", 1)[1]
            if _num.isdigit():
                rules[rule_id]["helpUri"] = (
                    "https://cwe.mitre.org/data/definitions/"
                    f"{_num}.html")
        results.append({
            "ruleId": rule_id,
            "level": _LEVEL.get(f.get("severity"), "warning"),
            "rank": _RANK.get(f.get("severity"), 5.0),
            "message": {"text": f"{f.get('title')} - "
                               f"{f.get('description', '')}"},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": str(f.get("url") or "")}}}],
            "partialFingerprints": {
                "argus/finding": f.get("id", "?"),
                "argus/category": f.get("category", ""),
            },
            "properties": {
                "argus-severity": f.get("severity", ""),
                "cvss": f.get("cvss", ""),
                "cwe": cwe,
                "owasp": f.get("owasp") or _owasp_of(cwe),
                "evidence_ids": f.get("evidence_ids", []),
                "evidence_excerpt":
                    str(f.get("evidence_excerpt") or "")[:500],
                "remediation": f.get("remediation", ""),
                "agent": f.get("agent", ""),
            },
        })
    doc = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [{
            "tool": {"driver": {
                "name": "Argus",
                "version": "1.0.0",
                "informationUri":
                    "https://github.com/TranTien2205/ctf",
                "rules": list(rules.values()),
            }},
            "results": results,
            "invocations": [{
                "executionSuccessful": True,
                "startTimeUtc": time.strftime(
                    "%Y-%m-%dT%H:%M:%SZ", time.gmtime(session.started)),
            }],
        }],
    }
    path = session.dir / "report.sarif"
    from ..session import _atomic_write
    _atomic_write(path, json.dumps(doc, indent=2, ensure_ascii=False))
    return path
