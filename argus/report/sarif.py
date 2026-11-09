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


# SARIF 2.1.0: `level` is meaningful only when `kind` is "fail". Anything this
# system has not proven is a "review" result at level "none" - a candidate that
# entered a dashboard as an error would fail a build on evidence the project
# itself grades as incomplete, which is the opposite of the point.
_KIND = {"proven": "fail", "candidate": "review", "unproven": "review",
         "refused": "informational"}


def render_sarif(session: Session) -> Path:
    sev_order = list(_LEVEL)
    grade_order = {"proven": 0, "candidate": 1, "unproven": 2, "refused": 3}
    findings = sorted(sanitized_findings(session.findings), key=lambda f: (
        grade_order.get(f.get("grade") or "", 0),
        sev_order.index(f.get("severity"))
        if f.get("severity") in sev_order else len(sev_order)))
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
        grade = str(f.get("grade") or "").strip().lower()
        # An unrecognized or absent grade defaults to "review", not "fail".
        # Defaulting to fail promoted an ungraded legacy finding - and any row
        # whose grade was edited to something unknown - into a CI build break.
        # "review", never "fail", for a grade we do not recognise. An ungraded
        # row - legacy, or one whose grade was stripped - is a thing we do not
        # know about, and breaking a build on it is worse than understating it.
        kind = _KIND.get(grade, "review")
        verdict = f.get("proof") if isinstance(f.get("proof"), dict) else {}
        missing = [str(m) for m in (verdict.get("missing") or [])]
        prefix = "" if kind == "fail" else f"[{grade.upper()}] "
        results.append({
            "ruleId": rule_id,
            "kind": kind,
            "level": _LEVEL.get(f.get("severity"), "warning")
            if kind == "fail" else "none",
            "rank": _RANK.get(f.get("severity"), 5.0)
            if kind == "fail" else -1.0,
            "message": {"text": prefix + f"{f.get('title')} - "
                               f"{f.get('description', '')}"
                        + (f" [unmet proof checks: {', '.join(missing)}]"
                           if missing else "")},
            "locations": [{"physicalLocation": {
                "artifactLocation": {"uri": str(f.get("url") or "")}}}],
            "partialFingerprints": {
                "argus/finding": f.get("id", "?"),
                "argus/category": f.get("category", ""),
            },
            "properties": {
                "argus-severity": f.get("severity", ""),
                "argus-grade": grade,
                "argus-vuln-class": f.get("vuln_class", ""),
                "argus-proof-requirement": str(verdict.get("requirement") or ""),
                "argus-proof-missing": missing,
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
