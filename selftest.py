#!/usr/bin/env python3
"""Offline self-check: spins the lab and drives a scripted agent over it.

Proves, without an API key, that scope enforcement, probes, evidence gating,
the loop and the report generator all work. For a real-model smoke run use:

    python -m argus run http://127.0.0.1:8777 --goal "map and test everything"

after starting `python lab/vulnapp.py 8777`.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab"))

PASS, FAIL = "PASS", "FAIL"
results: list[tuple[str, str]] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    results.append((PASS if ok else FAIL, f"{name}{' - ' + detail if detail else ''}"))


def main() -> int:
    import vulnapp
    srv = vulnapp.make_server(0)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    time.sleep(0.3)
    base = f"http://127.0.0.1:{srv.server_address[1]}"

    # --- unit-level checks ----------------------------------------------
    from argus.scope import ScopeError, ScopeGuard
    g = ScopeGuard("https://t.example", allow_private=False)
    check("scope allows in-scope", _ok(lambda: g.check("https://t.example/x")))
    check("scope denies foreign host",
          _raises(ScopeError, lambda: g.check("https://e.example")))
    check("scope denies file scheme",
          _raises(ScopeError, lambda: g.check("file:///etc/passwd")))

    from argus.session import Session
    tmp = Path(tempfile.mkdtemp())
    s = Session(tmp, base, meta={})
    rid = s.record_exchange("t", {}, {"status": 200, "body": "root:x:0:0"})
    check("finding accepts verbatim evidence",
          _ok(lambda: s.add_finding("t", "low", "x", "u", [rid], "root:x", "d", "r")))
    check("finding rejects invented evidence",
          _raises(ValueError, lambda: s.add_finding(
              "t", "low", "x", "u", [rid], "not-present", "d", "r")))

    # --- probe checks against live lab -----------------------------------
    from argus.config import Config
    from argus.httpclient import GuardedClient
    from argus.ratelimit import RateLimiter
    from argus.tools import Context, probes, web

    cfg = Config(target=base, allow_private=True, session_dir=tmp)
    scope = ScopeGuard(base, allow_private=True)
    client = GuardedClient(scope, s, RateLimiter(0), max_requests=300)
    ctx = Context(cfg=cfg, scope=scope, session=s, client=client,
                  skills_dir=ROOT / "argus" / "skills")

    out = web.fingerprint(ctx, base)
    check("fingerprint reads stack", any("LabVuln" in h for h in out["stack_hints"]))
    out = web.crawl(ctx, base, depth=1)
    check("crawl finds forms/endpoints", len(out["endpoints"]) >= 4)
    out = probes.probe_reflection(ctx, base + "/search?q=x", "q")
    check("reflection probe sees XSS", out.get("reflected") is True)
    out = probes.probe_sqli(ctx, base + "/item?id=1", "id")
    check("sqli probe sees candidate", "candidate" in out["verdict"])
    out = probes.probe_time(ctx, base + "/ping?host=1", "host", delay_s=2)
    check("time probe sees cmd delay", "cmd" in out["verdict"])
    out = probes.probe_ssti(ctx, base + "/hello?name=x", "name")
    check("ssti probe sees eval", "ssti candidate" in out["verdict"])
    out = probes.probe_lfi(ctx, base + "/download?file=x", "file")
    check("lfi probe sees file bytes", "confirmed marker" in out["verdict"])
    out = probes.probe_redirect(ctx, base + "/redirect?next=/", "next")
    check("redirect probe sees open redirect", out["verdict"] == "open redirect")
    out = probes.probe_cors(ctx, base + "/api/data")
    check("cors probe sees credentialed reflection",
          "credentials" in out["verdict"])

    # --- end-to-end loop with a scripted model ---------------------------
    from argus.llm import ScriptedClient
    from argus.loop import AgentLoop
    # probe_sqli is the loop's first call: r1 baseline, r2 quote->error body
    script = [
        {"tool_calls": [{"id": "c1", "name": "probe_sqli", "type": "tool_use",
                         "input": {"url": base + "/item?id=1", "param": "id"}}]},
        {"tool_calls": [{"id": "c2", "name": "record_finding", "type": "tool_use",
                         "input": {"title": "SQLi /item", "severity": "high",
                                   "category": "sqli", "url": base + "/item",
                                   "evidence_ids": ["r2"],
                                   "evidence_excerpt": "sqlite3.OperationalError",
                                   "description": "error channel sql injection",
                                   "remediation": "parameterize"}}]},
        {"tool_calls": [{"id": "c3", "name": "finish", "type": "tool_use",
                         "input": {"summary": "selftest run"}}]},
    ]
    cfg2 = Config(target=base, allow_private=True, session_dir=tmp,
                  max_turns=10, rate_rps=0)
    result = AgentLoop(cfg2, llm=ScriptedClient(script), quiet=True).run()
    check("agent loop completes", result["findings"] == 1,
          f"report={result['report']}")
    check("report renders evidence",
          Path(result["report"]).exists()
          and "sqlite3.OperationalError" in Path(result["report"]).read_text())

    client.close()
    srv.shutdown()

    print("\n=== argus selftest ===")
    for status, line in results:
        print(f"[{status}] {line}")
    failed = [r for r in results if r[0] == FAIL]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    return 1 if failed else 0


def _ok(fn) -> bool:
    try:
        fn()
        return True
    except Exception:
        return False


def _raises(exc, fn) -> bool:
    try:
        fn()
        return False
    except exc:
        return True
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(main())
