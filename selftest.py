#!/usr/bin/env python3
"""Offline self-check: spins the lab and drives a scripted agent over it.

Proves, without an API key, that scope enforcement, probes, evidence gating,
the loop and the report generator all work. For a real-model smoke run use:

    python -m argus run http://127.0.0.1:8777 --goal "map and test everything"

after starting `python lab/vulnapp.py 8777`.
"""
from __future__ import annotations

import json
import re
import os
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
    check("finding dedups same class+endpoint",
          _raises(ValueError, lambda: s.add_finding(
              "t2", "low", "x", "u", [rid], "root:x", "d", "r")))

    from argus.session import verify_transcript
    res = verify_transcript(s.dir)
    check("transcript hash chain verifies",
          res["chained"] and not res["bad_lines"])
    tpath = s.dir / "transcript.jsonl"
    orig = tpath.read_text(encoding="utf-8")
    lines = orig.splitlines()
    e = json.loads(lines[0]); e["x"] = "edited"
    lines[0] = json.dumps(e, ensure_ascii=False)
    tpath.write_text("\n".join(lines) + "\n", encoding="utf-8")
    check("tampered line is flagged",
          verify_transcript(s.dir)["bad_lines"] == [1])
    tpath.write_text(orig, encoding="utf-8")  # restore for the suite

    s2 = Session(Path(tempfile.mkdtemp()), base, meta={},
                 secrets=["sup3rsecr3t"])
    s2.record_exchange("t", {"body": "u=a&p=sup3rsecr3t"},
                       {"status": 200, "body": "ok"})
    raw = (s2.dir / "transcript.jsonl").read_text(encoding="utf-8")
    check("declared secret scrubbed from persisted bodies",
          "sup3rsecr3t" not in raw and "redacted" in raw)

    # basic-auth creds embedded in a URL must not persist either
    s2.record_exchange(
        "t", {"url": "http://admin:s3cretP4ss@h/login",
              "method": "GET"}, {"status": 200, "body": "x"})
    raw2 = (s2.dir / "transcript.jsonl").read_text(encoding="utf-8")
    check("url userinfo scrubbed from transcript",
          "s3cretP4ss" not in raw2 and "redacted" in raw2)

    # --- probe checks against live lab -----------------------------------
    from argus.config import Config
    from argus.httpclient import GuardedClient
    from argus.ratelimit import RateLimiter
    from argus.tools import Context, probes, web

    cfg = Config(target=base, allow_private=True, session_dir=tmp)
    scope = ScopeGuard(base, allow_private=True)
    # 600: the probes legitimately send more now - ssti sends a second operand
    # pair because one product can be a coincidence, cmdi takes a second
    # baseline and re-sends a slow family before calling it a delay, and
    # lockout needs a counted series. The budget is the harness's, not a claim
    # about the system.
    client = GuardedClient(scope, s, RateLimiter(0), max_requests=600)
    ctx = Context(cfg=cfg, scope=scope, session=s, client=client,
                  skills_dir=ROOT / "argus" / "skills")

    from argus.tools.analysis import (_curl_arg_check, _nmap_arg_check,
                                      _ffuf_arg_check, _sqlmap_arg_check,
                                      _nuclei_arg_check)
    check("curl guard blocks file exfil",
          bool(_curl_arg_check(ctx, ["-d", "@/etc/passwd", base])) and
          bool(_curl_arg_check(ctx, ["-F", "f=@cfg", base])))
    check("curl guard blocks config+proxy+redirect",
          bool(_curl_arg_check(ctx, ["-K", "cfg", base])) and
          bool(_curl_arg_check(ctx, ["-x", "http://p:8080", base])) and
          bool(_curl_arg_check(ctx, ["--resolve", "x:80:1.2.3.4", base])))
    check("curl guard parses bundled shorts",
          bool(_curl_arg_check(ctx, ["-sK", "cfg", base])) and
          bool(_curl_arg_check(ctx, ["-sd@x", base])))
    check("curl guard allows plain args",
          _curl_arg_check(ctx, ["-sS", "-d", "a=b@c.d", base]) is None)
    check("sqlmap guard blocks --eval/-d/tamper-path",
          bool(_sqlmap_arg_check(ctx, ["-u", base, "--eval", "x"])) and
          bool(_sqlmap_arg_check(ctx, ["-u", base, "-d", "mysql://a@b/"])) and
          bool(_sqlmap_arg_check(ctx, ["-u", base, "--tamper", "../x.py"])))
    check("sqlmap guard blocks -z/--alert local exec",
          bool(_sqlmap_arg_check(ctx, ["-u", base, "-z", "eva=print(1)"])) and
          bool(_sqlmap_arg_check(ctx, ["-u", base, "--alert", "beep"])))
    check("ffuf guard confines wordlists",
          bool(_ffuf_arg_check(ctx, ["-w", "/etc/passwd:FUZZ", "-u", base])))
    check("ffuf guard blocks -input-cmd local exec",
          bool(_ffuf_arg_check(ctx, ["-input-cmd", "id", "-u", base])))
    check("nuclei guard blocks lfa/custom-oob",
          bool(_nuclei_arg_check(ctx, ["-lfa", "-u", base])) and
          bool(_nuclei_arg_check(ctx, ["-iserver", "http://oob.example"])))
    check("nmap guard blocks -iR and script paths",
          bool(_nmap_arg_check(ctx, ["-iR", "100"])) and
          bool(_nmap_arg_check(ctx, ["--script", "./x.nse", "127.0.0.1"])))
    tf = tmp / "evil.yaml"
    tf.write_text("id: x\n")
    check("nuclei guard blocks template files+code",
          bool(_nuclei_arg_check(ctx, ["-t", str(tf), "-u", base])) and
          bool(_nuclei_arg_check(ctx, ["-code", "-u", base])))
    from argus.tools.analysis import run_external
    check("external rejects non-allowlisted tool",
          "not allowed" in (run_external(ctx, "hydra", base).get("error") or ""))
    check("external scope-checks target host",
          "scope" in (run_external(ctx, "curl", "http://foreign.example")
                      .get("error") or "").lower())
    from argus.tools.analysis import read_response
    rr = ctx.client.send("GET", base + "/", tool="selftest")
    page = read_response(ctx, rr["request_id"], offset=0, length=4000)
    check("read_response pages a recorded body",
          "LabShop" in page["body"] and page["status"] == 200)
    check("read_response rejects unknown id",
          "error" in read_response(ctx, "r99999"))

    from argus.tools.analysis import jwt_decode, jwt_forge
    import json as _json
    tok = _json.loads(ctx.client.send(
        "GET", base + "/token?user=alice", tool="selftest")["body"])["token"]
    dec = jwt_decode(ctx, tok)
    check("jwt_decode recovers weak secret",
          dec.get("recovered_secret") == "secret123")
    forged = jwt_forge(ctx, tok, '{"user":"admin","role":"admin"}',
                       secret=dec["recovered_secret"])
    me = ctx.client.send(
        "GET", base + "/api/me",
        headers={"Authorization": "Bearer " + forged["resigned"]},
        tool="selftest")
    check("jwt_forge mints accepted admin token",
          '"role": "admin"' in (me.get("body") or ""))

    out = web.fingerprint(ctx, base)
    check("fingerprint reads stack", any("LabVuln" in h for h in out["stack_hints"]))
    out = web.fingerprint(ctx, base + "/login")
    check("fingerprint reads cookie framework hint",
          any("php" in h and "PHPSESSID" in h for h in out["stack_hints"])
          and any(c["name"] == "PHPSESSID" and not c["samesite"]
                  for c in out["cookies"]))
    check("fingerprint flags session-cookie hygiene",
          any("HttpOnly" in n for n in out["cookie_notes"]))
    out = web.fingerprint(ctx, base + "/bad-headers")
    _hn = " ".join(out["header_notes"])
    check("fingerprint flags bad header values",
          all(t in _hn for t in ("x-frame-options",
                                 "strict-transport-security",
                                 "content-security-policy")))
    out = web.graphql_introspect(ctx, base + "/graphql")
    check("graphql introspects schema + GET transport",
          out["verdict"].startswith("schema introspected")
          and out["get_transport"] is True)
    out = web.graphql_introspect(ctx, base + "/graphql-strict")
    check("graphql suggestion leak when introspection off",
          out["suggestion_leak"] is True)
    out = web.crawl(ctx, base, depth=1)
    check("crawl finds forms/endpoints", len(out["endpoints"]) >= 4)
    out = web.js_recon(ctx, base)
    check("js_recon recovers sourcemap", out["sourcemaps_found"] == 1
          and any("/api/admin/export" in e["endpoint"]
                  for e in out["endpoints"]))
    out = probes.probe_reflection(ctx, base + "/search?q=x", "q")
    check("reflection probe sees XSS", out.get("reflected") is True)
    out = probes.probe_sqli(ctx, base + "/item?id=1", "id")
    check("sqli probe sees candidate", "candidate" in out["verdict"])
    out = probes.probe_sqli(ctx, base + "/product?id=1", "id")
    check("sqli probe sees numeric-context", "numeric context" in out["verdict"])
    out = probes.probe_sqli(ctx, base + "/stock?sku=x", "sku")
    check("sqli probe sees or-pair", "OR pair" in out["verdict"])
    out = probes.probe_sqli(ctx, base + "/item?id=1", "id", union_cols=6)
    check("sqli probe bounds union columns",
          out["union"]["columns"] == 2)
    out = probes.probe_time(ctx, base + "/ping?host=1", "host", delay_s=2)
    check("time probe sees cmd delay", "cmd" in out["verdict"])
    slow = {r["family"] for r in out["results"] if r["slow"]}
    check("time probe sees sql delays",
          {"mysql", "postgres", "mssql", "mysql-benchmark"} <= slow)
    out = probes.probe_ssti(ctx, base + "/hello?name=x", "name")
    check("ssti probe sees eval", "ssti candidate" in out["verdict"])
    out = probes.probe_ssti(ctx, base + "/hello2?name=x", "name")
    check("ssti probe sees eval-and-reflect",
          "ssti candidate" in out["verdict"]
          and any(r.get("also_reflected") for r in out["results"]))
    out = probes.probe_lfi(ctx, base + "/download?file=x", "file")
    check("lfi probe sees file bytes", "confirmed marker" in out["verdict"])
    out = probes.probe_redirect(ctx, base + "/redirect?next=/", "next")
    check("redirect probe sees open redirect",
          "open redirect" in out["verdict"])
    check("redirect probe flags javascript: scheme Location",
          "javascript:" in out["verdict"])
    out = probes.probe_redirect(ctx, base + "/jsredirect?next=/", "next")
    check("redirect probe sees client-side", "client-side" in out["verdict"])
    out = probes.probe_redirect(ctx, base + "/safedirect?next=/", "next")
    check("redirect probe bypasses path filter",
          "protocol-relative" in out["verdict"])
    out = probes.probe_lockout(ctx, base + "/login2",
                               data="username=x&password=y")
    check("lockout probe flags unthrottled login",
          "no lockout" in out["verdict"])
    out = probes.probe_lockout(ctx, base + "/login3",
                               data="username=x&password=y")
    check("lockout probe sees throttled login",
          "throttling observed" in out["verdict"])
    out = probes.probe_massassign(
        ctx, base + "/api/register",
        data='{"username":"st1","password":"x"}')
    check("massassign probe sees bound privilege fields",
          "mass-assignment candidate" in out["verdict"])
    out = probes.probe_csrf(ctx, base + "/api/config", data="theme=x")
    check("csrf probe sees text/plain replay", "text/plain" in out["verdict"])
    out = probes.probe_cors(ctx, base + "/api/data")
    check("cors probe sees credentialed reflection",
          "credentials" in out["verdict"])
    check("cors probe sees null-origin trust",
          "null origin" in out["verdict"])
    check("cors probe sees preflight reflection",
          "preflight" in out["verdict"])
    out = probes.probe_idor(ctx, base + "/api/user/2")
    check("idor probe flags neighboring object", "idor candidate" in out["verdict"])
    out = probes.probe_ssrf(ctx, base + "/fetch?url=x", "url")
    check("ssrf probe sees self-fetch", "ssrf" in out["verdict"])
    # The lab used to pass /fetch's parameter straight to urlopen, so this
    # check asserted that the probe could read the OPERATOR'S real
    # /etc/passwd. That is the behaviour the `cat` allowlist exists to
    # prevent, through a different door. The lab now refuses a non-http
    # scheme, and what the probe must still see is the internal-only
    # response - the metadata fixture - because that is what an SSRF proof
    # rests on.
    check("ssrf probe is refused the file scheme",
          not any(h["marker"] for h in out["results"]
                  if h["name"].startswith("file")))
    check("ssrf probe sees an internal-only response",
          any(h["marker"] for h in out["results"]
              if "metadata" in h["name"] or "aws" in h["name"]
              or "169.254" in str(h.get("payload", ""))))
    out = probes.probe_xxe(ctx, base + "/xml")
    check("xxe probe resolves entity", "xxe candidate" in out["verdict"])
    out = probes.probe_csrf(ctx, base + "/login")
    check("csrf probe flags tokenless form", "csrf" in out["verdict"])
    out = probes.probe_csrf(ctx, base + "/")
    check("csrf probe flags get-form state change",
          "get form" in out["verdict"].lower()
          and "state-changing" in out["verdict"])
    out = probes.probe_enum(ctx, base + "/login",
                            "username=x&password=x", "username")
    check("enum probe sees user differential",
          "enumeration candidate" in out["verdict"])
    out = probes.probe_enum(ctx, base + "/login2",
                            "username=x&password=x", "username",
                            users="admin,bob")
    check("enum probe sees timing differential",
          "timing" in out["verdict"] or "candidate" in out["verdict"])
    out = probes.probe_xfh(ctx, base + "/reset")
    check("xfh probe sees reflected host", "candidate" in out["verdict"])
    out = probes.probe_xfh(ctx, base + "/", restricted="/admin")
    check("xfh probe sees x-original-url bypass",
          "acl-bypass candidate" in out["verdict"])
    out = probes.probe_nosqli(ctx, base + "/api/login",
                              '{"username":"admin","password":"x"}', "password")
    check("nosqli probe flips auth", "nosqli candidate" in out["verdict"])
    check("nosqli urlencoded operator flips",
          any(h["op"] == "urlencoded[$ne]" and h["differs"]
              for h in out["results"]))
    out = probes.probe_upload(ctx, base + "/upload")
    check("upload probe serves active file",
          "unrestricted upload" in out["verdict"])
    client.send("GET", base + "/redeem/reset", tool="http_request",
                note="reset the coupon")  # shared process state
    out = probes.probe_race(ctx, base + "/redeem", n=8)
    # Concurrency is the one thing here that depends on wall clock, and a
    # loaded runner serialises the burst - all three Windows CI jobs failed
    # this way once. The probe reports which happened, so check that it
    # reported honestly rather than that the machine cooperated.
    if out["verdict"].startswith("race:"):
        check("race probe multi-redeems", out["overlapped"] is True)
        check("race probe records the serial refusal",
              bool(out["serial_statuses"])
              and all(s >= 400 for s in out["serial_statuses"]))
    else:
        check("race probe says so when it saw no race",
              "inconclusive" in out["verdict"]
              or "no race window" in out["verdict"]
              or "repeatable" in out["verdict"], out["verdict"][:90])
        check("race probe reports the burst timing either way",
              isinstance(out.get("burst_seconds"), (int, float)))
    out = probes.probe_race(ctx, base + "/hello", n=6)
    check("race probe rejects repeatable", "repeatable" in out["verdict"])
    out = probes.probe_deserialize(ctx, base + "/import?data=x", "data")
    check("deserialize probe sees parser error",
          "deserialization surface" in out["verdict"])
    out = probes.probe_cache(ctx, base + "/cached")
    check("cache probe sees unkeyed xfh", "candidate" in out["verdict"])
    out = probes.probe_cache(ctx, base + "/profile")
    check("cache probe flags path confusion",
          "path confusion" in out["verdict"] and out["deception"])
    out = probes.probe_ppoll(ctx, base + "/api/config",
                             base + "/api/config")
    check("ppoll probe sees merged key",
          "prototype-pollution candidate" in out["verdict"])
    out = probes.probe_ppoll(ctx, base + "/api/config2",
                             base + "/api/config")
    check("ppoll probe sees constructor carrier",
          "constructor.prototype" in out["verdict"])
    out = probes.probe_smuggle(ctx, base + "/desync")
    check("smuggle probe sees cl.te desync",
          "cl.te desync" in out["verdict"]
          and bool(out.get("ambiguous_id")) and bool(out.get("check_id")))
    out = probes.probe_smuggle(ctx, base + "/desync-cl")
    check("smuggle probe sees te.cl desync",
          "te.cl desync" in out["verdict"]
          and bool(out.get("ambiguous_id")) and bool(out.get("check_id")))
    out = probes.probe_smuggle(ctx, base + "/desync-obf")
    check("smuggle probe sees obfuscated-te desync",
          "obfuscated TE" in out["verdict"])
    out = probes.probe_smuggle(ctx, base + "/desync-none")
    check("smuggle probe clean on agreed framing",
          "no desync signal" in out["verdict"])
    out = probes.probe_crlf(ctx, base + "/redirect?next=/", "next")
    check("crlf probe injects header",
          out["injected_header"] and "crlf injection" in out["verdict"])
    check("crlf probe cites a control for the comparison",
          bool(out.get("control_id")))
    out = probes.probe_disclosure(ctx, base)
    check("disclosure probe finds exposed paths",
          {h["path"] for h in out["exposed"]} >= {"/.git/HEAD", "/.env", "/debug"})
    out = probes.probe_websocket(ctx, base + "/ws")
    check("websocket probe completes the cross-origin handshake",
          out["accept_ok"] and bool(out["handshake_id"]))
    check("websocket probe gets a frame back carrying its nonce",
          out["answered"] and out["canary"] in out["reply"])
    out = probes.probe_websocket(ctx, base + "/ws-strict")
    check("websocket probe is refused where Origin is checked",
          not out["accept_ok"] and out["status"] == 403)
    out = probes.probe_method(ctx, base + "/")
    check("method probe sees TRACE echo",
          out.get("trace_attempt", {}).get("echoes") is True)

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
    sj = json.loads((Path(result["report"]).parent / "summary.json")
                    .read_text(encoding="utf-8"))
    check("summary carries run metrics",
          "time_to_first_finding_s" in sj and sj.get("llm_calls") == 3)

    # --- audit guarantees added after the original selftest ---------------
    sdir = Path(result["report"]).parent
    check("finding carries auto-mapped CWE",
          json.loads((sdir / "findings.json").read_text())[0]
          .get("cwe") == "CWE-89")
    check("finding carries OWASP Top10 bucket",
          json.loads((sdir / "findings.json").read_text())[0]
          .get("owasp") == "A03 Injection"
          and "OWASP Top 10" in (sdir / "report.md").read_text())
    sarif = json.loads((sdir / "report.sarif").read_text())
    check("report.sarif is valid 2.1.0",
          sarif["version"] == "2.1.0"
          and sarif["runs"][0]["results"][0]["ruleId"] == "CWE-89")
    from argus.report.markdown import _fence
    evil = "x\n```\n# FAKE\n```\ny"
    check("report fence survives backtick injection",
          _fence(evil) == "````" and _fence("clean") == "```")
    from argus.session import verify_transcript
    res = verify_transcript(sdir)
    check("verify re-validates findings ok", res["findings_checked"] == 1
          and not res.get("findings_bad"))
    fp = sdir / "findings.json"
    orig_bytes = fp.read_bytes()
    fs = json.loads(orig_bytes)
    fs[0]["evidence_excerpt"] = "tampered-bytes"
    fp.write_text(json.dumps(fs))
    res = verify_transcript(sdir)
    check("verify flags tampered finding", res.get("findings_bad") == ["F01"])
    check("seal flags findings.json edit",
          res.get("artifact_mismatch") == ["findings.json"])
    fs[0]["evidence_excerpt"] = "sqlite3.OperationalError"
    fp.write_text(json.dumps(fs))
    res = verify_transcript(sdir)
    check("content-identical rewrite still flagged by seal",
          res.get("artifact_mismatch") == ["findings.json"])
    fp.write_bytes(orig_bytes)  # byte-exact restore
    res = verify_transcript(sdir)
    check("seal clean after byte-exact restore",
          not res.get("artifact_mismatch"))
    mp = sdir / "meta.json"
    m_orig = mp.read_bytes()
    mp.write_bytes(m_orig + b" ")
    res = verify_transcript(sdir)
    check("seal flags meta.json whitespace edit",
          res.get("artifact_mismatch") == ["meta.json"])
    mp.write_bytes(m_orig)
    from argus.loop import _compact_history, _KEEP_FULL_RESULTS
    msgs = [{"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": "c",
         "content": json.dumps({"request_id": "r1", "x": "y" * 500})}]}]
    for i in range(_KEEP_FULL_RESULTS):
        msgs.append({"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": f"k{i}",
             "content": "z" * 500}]})
    _compact_history(msgs)
    check("history compacts old results keeping rids",
          "rids: r1" in msgs[0]["content"][0]["content"]
          and msgs[-1]["content"][0]["content"] == "z" * 500)

    # --- MCP bridge (fake stdio server) -----------------------------------
    from argus.mcp import MCPManager
    from argus.tools import mcp_tools
    mcfg = tmp / "mcp.json"
    mcfg.write_text(json.dumps({"servers": {"fake": {
        "command": [sys.executable,
                    str(ROOT / "tests" / "fake_mcp_server.py")]}}}))
    mgr = MCPManager(mcfg)
    try:
        ctx.mcp = mgr
        out = mcp_tools.mcp_call(ctx, "fake", "echo", {"hi": 1})
        check("mcp_call roundtrips via stdio", "echo:" in out.get("output", ""))
        out = mcp_tools.mcp_call(ctx, "ghost", "x", {})
        check("mcp_call unknown server errors", "error" in out)
    finally:
        mgr.close()

    # --- team mode: lead pipeline + role gating + exploit runner ----------
    from argus.team.board import Board
    from argus.team.leads import Lead, LeadQueue
    from argus.tools import team as teamtools

    q = LeadQueue()
    check("lead queue dedups and says which refusal applied",
          q.offer(Lead(kind="endpoint", url=base + "/a")) == ""
          and q.offer(Lead(kind="endpoint", url=base + "/a")) == "duplicate",
          "a closed pipeline and a spent bound are refusals too, and a "
          "producer told 'duplicate' for either one goes looking for "
          "different surface instead of stopping")
    q.close()
    leads, closed = q.pull(wait_s=0)
    check("lead queue drains on close", len(leads) == 1)
    _, closed = q.pull(wait_s=0)
    check("lead queue reports closed+empty", closed is True)

    ctx.board = Board(s)
    out = teamtools.emit_lead(ctx, kind="endpoint", url=base + "/item?id=1",
                              params=["id"])
    check("emit_lead queues in-scope work", out.get("queued") is True)
    out = teamtools.emit_lead(ctx, kind="endpoint", url="http://x.invalid/")
    check("emit_lead rejects out-of-scope", "error" in out)
    out = teamtools.wordlist_fuzz(ctx, base_url=base, wordlist="api-paths",
                                  max_words=10)
    check("wordlist_fuzz hits hidden paths",
          out["tested"] == 10 and len(out["interesting"]) >= 1)
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", base)
    check("exploit runner proves manifest", out.get("proof") is True)
    out = teamtools.run_exploit(ctx, "lab-jwt-forge", base)
    check("exploit runner proves jwt forge", out.get("proof") is True)
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", "http://x.invalid/")
    check("exploit runner scope-checks target", "error" in out)

    # --- ambient-trust hardening --------------------------------------
    # the target-facing client must ignore env proxies and ~/.netrc:
    # credentials must never ride the wire without a declared input
    os.environ.setdefault("HTTP_PROXY", "http://127.0.0.1:9")
    check("target client ignores env proxy/netrc",
          client._client._trust_env is False)

    # a cwd resources/exploits manifest names commands to run - it must
    # be opt-in or a planted manifest executes via the model
    _cwd = Path.cwd()
    _fake = Path(tempfile.mkdtemp())
    (_fake / "resources" / "exploits" / "evil").mkdir(parents=True)
    (_fake / "resources" / "exploits" / "evil" / "manifest.json"
     ).write_text('{"command": ["calc"]}', encoding="utf-8")
    try:
        os.chdir(_fake)
        import importlib
        importlib.reload(teamtools)
        m, _d, err = teamtools._load_manifest("evil")
        check("cwd exploit manifest refused by default",
              m is None and err is not None)
        os.environ["ARGUS_EXPLOITS_CWD"] = "1"
        m, _d, err = teamtools._load_manifest("evil")
        check("cwd exploit honored with opt-in",
              m == {"command": ["calc"]})
        del os.environ["ARGUS_EXPLOITS_CWD"]
    finally:
        os.chdir(_cwd)
        importlib.reload(teamtools)

    # a cwd mcp.json names subprocesses - ignored unless ARGUS_MCP_CWD=1
    from argus.mcp import discover_config_path
    _fake2 = Path(tempfile.mkdtemp())
    (_fake2 / "mcp.json").write_text(
        '{"servers": {"x": {"command": ["calc"]}}}', encoding="utf-8")
    _cwd2 = Path.cwd()
    try:
        os.chdir(_fake2)
        check("cwd mcp.json refused by default",
              discover_config_path() is None)
        os.environ["ARGUS_MCP_CWD"] = "1"
        check("cwd mcp.json honored with opt-in",
              discover_config_path() == Path("mcp.json"))
        del os.environ["ARGUS_MCP_CWD"]
    finally:
        os.chdir(_cwd2)

    # operator-input validation: startup flags fail fast with clean
    # errors instead of tracebacks deep in the runtime
    from argus.config import (_validate_proxy, _validate_resume,
                              _validate_session_dir)
    check("proxy socks5 rejected (no socksio)",
          _raises(SystemExit, lambda: _validate_proxy("socks5://x")))
    check("proxy scheme-garbage rejected",
          _raises(SystemExit, lambda: _validate_proxy("://bad")))
    check("proxy http accepted",
          _validate_proxy("http://127.0.0.1:8080") ==
          "http://127.0.0.1:8080")
    check("resume non-dir rejected",
          _raises(SystemExit,
                  lambda: _validate_resume("/nonexistent-argus-dir")))
    check("resume real session dir accepted",
          _validate_resume(str(s.dir)) == str(s.dir))
    _f = Path(tempfile.mktemp())
    _f.write_text("x")
    check("session-dir-as-file rejected",
          _raises(SystemExit, lambda: _validate_session_dir(_f)))
    from argus.mcp import MCPManager
    _badcfg = Path(tempfile.mktemp(suffix=".json"))
    _badcfg.write_text('{"servers": {"x": "not-an-object"}}')
    check("malformed mcp config yields per-entry errors",
          bool(MCPManager(_badcfg).errors()))

    client.close()
    srv.shutdown()

    # the doc gate appends its own results, so it must run BEFORE the print
    # loop. It used to run after, which meant a documentation failure was
    # counted but never printed: the gate reported 130/131 and said nothing
    # about which check failed, in the one subsystem whose entire claim is
    # that it names what is wrong.
    _doc_consistency()
    _doc_selftest_count()

    print("\n=== argus selftest ===")
    for status, line in results:
        print(f"[{status}] {line}")

    failed = [r for r in results if r[0] == FAIL]
    print(f"\n{len(results) - len(failed)}/{len(results)} passed")
    return 1 if failed else 0


def _doc_selftest_count() -> None:
    """The selftest count the docs state, checked against this run.

    It has to be the LAST check: at that moment `len(results)` is one short of
    the final tally, so `+1` is exact rather than a guess about how many
    checks are still to come. An earlier draft guessed, and was right by
    accident.
    """
    import re as _re
    joined = ""
    for name in ("CHANGELOG.md", "README.md", "AGENTS.md", "docs/USAGE.md",
                 "docs/ARCHITECTURE.md"):
        fp = ROOT / name
        if fp.is_file():
            joined += fp.read_text(encoding="utf-8")
    stated = {int(n) for n in _re.findall(r"(\d+) offline checks", joined)}
    total = len(results) + 1
    check(f"doc selftest count matches this run ({total})",
          bool(stated) and stated == {total},
          f"docs state {sorted(stated) or 'NO COUNT AT ALL'}, this run has "
          f"{total}")


# --- documentation names only things that exist ---------------------------
#
# This project's claim is that it does not invent endpoints, versions or
# numbers. A README naming a removed command, or a count that drifted when a
# tool was added, is the same defect in the documentation - and it is the one
# a reader checks first. So the docs are verified against the code, not
# proof-read.

# Nine files was 9 of the 40 tracked markdown files. The skills and the role
# cards are read by the MODEL at runtime, so a stale tool name in one of them
# is worse than a stale one in the README - it goes straight into a prompt.
_DOC_FILES = ("README.md", "AGENTS.md", "SECURITY.md", "CHANGELOG.md",
              "docs/ARCHITECTURE.md", "docs/USAGE.md", "docs/EXPERIMENTS.md",
              # It was the one docs/*.md outside this list, so NONE of the
              # checks below reached it - not the tool names, not the flags,
              # not the subcommands, not the counts. The document whose
              # whole purpose is to let a reader check a claim rather than
              # take it was the one document nothing checked.
              "docs/VERIFICATION.md",
              "lab/README.md", "argus/skills/INDEX.md",
              "argus/resources/exploits/README.md",
              "argus/resources/wordlists/README.md",
              "argus/team/roles/lead.md", "argus/team/roles/recon.md",
              "argus/team/roles/exploit.md", "argus/team/roles/report.md",
              ".env.example")

# words that look like a tool name but are not one
# Identifiers that LOOK like tools - they share a prefix with a tool family -
# and are not: module names, transcript fields, helper functions. The check
# cannot tell `probe_sqli` from `run_id` by syntax, so this list is the
# mechanism rather than a workaround; what keeps it honest is the check below
# that every entry is still named in a doc. Ten entries had gone dead.
# The env lookups argus/ actually performs, for the `.env.example`
# completeness check. Built here rather than inline so the character
# class for the two quote styles stays readable.
_ENV_READ_RE = re.compile(
    r'(?:environ(?:\.get)?|getenv)\(\s*[\x22\x27]'
    r'(ARGUS_[A-Z0-9_]+|ANTHROPIC_[A-Z0-9_]+|CLAUDE_[A-Z0-9_]+)')


_NOT_TOOLS = {
    "probe_", "probe_x", "record_exchange", "record_event",
    "add_finding", "render_report", "verify_transcript",
    "findings_overgraded", "seal_artifacts", "make_server",
    "proof_marker",     "build_system", "time_to_first",
    # module and field names that share a prefix with a tool family:
    # `mcp_tools` is the module behind mcp_list/mcp_call, and `request_id(s)`
    # is the transcript field every probe returns
    "mcp_tools", "request_id", "request_ids", "request_text",
    "proof_requirement",     # transcript ids that survive history compaction - `run_id` shares the
    # `run_*` family with run_external/run_exploit and is not a tool
    "run_id", "call_id",
    # a probe PARAMETER, not a tool: probe_csrf takes `read_url` to bracket
    # the write with a read before and after
    "read_url",
    # a config loader, named in VERIFICATION.md as the mechanism that
    # rejects a non-finite budget. It shares the `load_*` family with
    # load_skill and is not a tool.
    "load_config",
}


def _doc_consistency() -> None:
    import re as _re
    import subprocess as _sub
    from argus.tools.registry import TOOL_SCHEMAS
    from argus.mcpserver import tool_manifest
    from argus import proof

    texts = {}
    for name in _DOC_FILES:
        fp = ROOT / name
        if fp.is_file():
            texts[name] = fp.read_text(encoding="utf-8")
    # every methodology module as well: load_skill puts these in front of the
    # model, so a tool it names has to exist
    for fp in sorted((ROOT / "argus" / "skills").glob("*.md")):
        texts[f"argus/skills/{fp.name}"] = fp.read_text(encoding="utf-8")
    # A hand-maintained list of documents cannot reveal a document nobody
    # added to it - the same error as counting a test table against the
    # features that have rows. `docs/VERIFICATION.md` escaped this gate
    # entirely that way, so the glob is the ground truth now.
    #     `docs/` was the first family to be derived this way; the rest of
    #     the tuple was still hand-listed, so a new role prompt - which
    #     `load_skill`'s sibling puts in front of a worker exactly as a
    #     skill module is - or a new top-level document would escape the
    #     gate the same way VERIFICATION.md did. `argus/skills/*.md` is
    #     already globbed into `texts` above and is not listed here.
    on_disk = set()
    for pattern in ("docs/*.md", "*.md", "lab/*.md",
                    "argus/team/roles/*.md", "argus/resources/*/README.md"):
        on_disk |= {p.relative_to(ROOT).as_posix()
                    for p in sorted(ROOT.glob(pattern)) if p.is_file()}
    ungated = sorted(on_disk - set(_DOC_FILES))
    check(f"every shipped document is in the gated set "
          f"({len(on_disk)} on disk)",
          not ungated,
          f"{ungated} exist but no check reads them - add them to "
          "_DOC_FILES or delete them")

    absent = sorted(n for n in _DOC_FILES if n not in texts)
    check(f"doc set is present ({len(_DOC_FILES)} named + "
          f"{len(texts) - len(_DOC_FILES) + len(absent)} skills)",
          not absent, f"missing {absent}")

    tool_names = {t["name"] for t in TOOL_SCHEMAS}

    # 1. every tool-shaped identifier in the docs is a registered tool.
    #    The names come from TOOL_SCHEMAS, not from a hand-written regex: the
    #    first version listed 43 of the 55 by hand, so a doc naming one of the
    #    other 12 was never checked at all.
    families = sorted({n.split("_", 1)[0] for n in tool_names if "_" in n}
                      | {n for n in tool_names if "_" not in n})
    ident_re = _re.compile(
        r"\b((?:" + "|".join(_re.escape(f) for f in families)
        + r")_[a-z0-9_]+)\b")
    unknown = {}
    for name, text in texts.items():
        for ident in set(ident_re.findall(text)):
            if ident not in tool_names and ident not in _NOT_TOOLS:
                unknown.setdefault(name, set()).add(ident)
    check(f"docs name only registered tools ({len(tool_names)})", not unknown,
          "; ".join(f"{k}: {sorted(v)}" for k, v in unknown.items()))
    # An exemption nothing needs is an invitation to add rather than check.
    # `_NOT_TOOLS` had grown to thirty entries, a third of them for words no
    # doc contained any more, so the list no longer described anything.
    _prefix_guards = {"probe_", "probe_x"}
    _all_doc_text = "\n".join(texts.values())
    stale = sorted(x for x in _NOT_TOOLS - _prefix_guards
                   if x not in _all_doc_text)
    check(f"every tool-name exemption is still needed "
          f"({len(_NOT_TOOLS)})", not stale,
          f"{stale} are exempted and named in no doc - delete them, so the "
          f"list says what it is for")

    # 2. every `argus <subcommand>` in the docs is a real subcommand
    # the add_parser calls wrap across lines, so read the file whole
    cli_src = (ROOT / "argus" / "cli.py").read_text(encoding="utf-8")
    real = set(_re.findall(r'sub\.add_parser\(\s*\n?\s*"([a-z-]+)"', cli_src))
    # only COMMAND-shaped mentions: `python -m argus <cmd>` or `argus <cmd>`
    # inside backticks. Prose like "argus as the server" is not a claim about
    # a subcommand, and treating it as one made this check cry wolf.
    named = set()
    for text in texts.values():
        named |= set(_re.findall(r"python -m argus ([a-z][a-z-]+)", text))
        named |= set(_re.findall(r"`argus ([a-z][a-z-]+)", text))
        # inside a fenced shell block the command often has no backticks and
        # no `python -m` prefix, which is where most examples live
        for block in _re.findall(r"```(?:bash|sh|console)?\n(.*?)```", text,
                                 _re.S):
            named |= set(_re.findall(r"(?m)^\s*(?:\$\s*)?argus\s+([a-z][a-z-]+)",
                                     block))
    bogus = sorted(n for n in named if n not in real)
    check(f"docs name only real subcommands ({len(real)})", not bogus,
          f"{bogus} not in {sorted(real)}")

    # 3. counts claimed in prose match the code
    joined = "\n".join(texts.values())
    claims = [
        ("tool", len(tool_names), _re.findall(r"(\d+)[- ]tools?\b", joined)
         + _re.findall(r"\b(\d+) of the (?:\d+) tools", joined)),
        ("class", len(proof.classes()),
         _re.findall(r"(\d+) (?:proof-matrix )?classes", joined)),
        ("skill", len(list((ROOT / "argus" / "skills").glob("*.md"))) - 1,
         _re.findall(r"(\d+) (?:loadable )?(?:methodology |knowledge )?modules",
                     joined)),
    ]
    served = len(tool_manifest())
    for label, actual, found in claims:
        nums = {int(n) for n in found}
        # `46 of the 56 tools` contributes both numbers legitimately
        allowed = {actual, served} if label == "tool" else {actual}
        wrong = sorted(nums - allowed)
        # A regex that stops matching would make this check pass forever on
        # nothing. If the docs no longer state the count anywhere, that is
        # itself the failure - say so rather than reporting success.
        check(f"doc {label} counts match the code ({actual})",
              bool(nums) and not wrong,
              f"docs state {sorted(nums) or 'NO COUNT AT ALL'}, "
              f"code has {sorted(allowed)}"
              + (f" - wrong: {wrong}" if wrong else ""))

    # 3b. every `--flag` the docs name is one a parser accepts. It checked no
    #     flags at all, so a doc naming `--max-depth` or `--target` passed.
    cli_src_all = (ROOT / "argus" / "cli.py").read_text(encoding="utf-8")
    cfg_src = (ROOT / "argus" / "config.py").read_text(encoding="utf-8")
    real_flags = set(_re.findall(r'add_argument\(\s*"(--[a-z0-9-]+)"',
                                 cli_src_all + cfg_src))
    real_flags |= {"--help", "--version", "--json", "--csv", "--team",
                   "--quiet"}
    # A flag named on the same LINE as one of the external tools argus drives
    # belongs to that tool, not to argus. Self-maintaining: the allowlist was a
    # hand-written set, and `--alert` (sqlmap's) was already outside it.
    from argus.tools.analysis import _ALLOWED_TOOLS
    # Decided PER LINE, which is what the rule above says and what the code
    # did not do. `foreign` used to be one set accumulated across every line
    # of every gated document and then subtracted globally, so a flag that
    # appeared once on a curl or nmap line was excused on every other line
    # in every other document - 11 names in the current tree, including
    # `--alert` and `--data-urlencode`, which no argus parser accepts.
    #
    # Measured before tightening: with the global union and with the
    # per-line rule, `invented` is empty either way, so this closes a hole
    # with no current occupant rather than fixing a live miss. That is the
    # cheapest moment to close one.
    doc_flags = set()
    flag_re = _re.compile(r"(?<![\w-])(--[a-z][a-z0-9-]{2,})")
    for name, text in texts.items():
        for line in text.splitlines():
            found = set(flag_re.findall(line))
            if not found:
                continue
            if any(t in line for t in _ALLOWED_TOOLS) \
                    or "docker" in line or "pip " in line:
                continue          # this line is about another tool
            doc_flags |= found
    invented = sorted(doc_flags - real_flags)
    check(f"docs name only real flags ({len(real_flags)})", not invented,
          f"{invented} accepted by no parser")

    # 3c. the test and selftest counts the docs state. I corrected both by
    #     hand six times in one session, which is exactly the kind of number
    #     that rots - so it is checked against a collection run, not trusted.
    import subprocess
    stated_tests = {int(n) for n in
                    _re.findall(r"pytest tests/ -q`?: (\d+) tests", joined)}
    if stated_tests:
        try:
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", "tests/", "--collect-only",
                 "-q"], cwd=str(ROOT), capture_output=True, text=True,
                timeout=180)
            m = _re.search(r"(\d+) tests? collected", proc.stdout)
            actual = int(m.group(1)) if m else 0
        except (OSError, subprocess.SubprocessError):
            actual = 0
        check(f"doc pytest count matches collection ({actual})",
              actual > 0 and stated_tests == {actual},
              f"docs state {sorted(stated_tests)}, collection finds {actual}"
              if actual else "could not collect; skipped")
    # 4. every ARGUS_* environment variable the docs name is one the code
    #    reads. Writing a plausible-looking opt-in flag into a README is the
    #    same defect as naming a removed command, and I made exactly that
    #    mistake while fixing the others.
    code = ""
    for src in (ROOT / "argus").rglob("*.py"):
        code += src.read_text(encoding="utf-8")
    # A variable named in `models.json` under `api_key_env` is read for real:
    # `models.Model.credential()` walks that list through os.environ. Grepping
    # only the .py files called ARGUS_LOCAL_API_KEY invented when it is the
    # one thing a local server needs set.
    for data in (ROOT / "argus").rglob("*.json"):
        code += data.read_text(encoding="utf-8", errors="replace")
    real_env = set(_re.findall(r"ARGUS_[A-Z0-9_]+", code))
    doc_env = set(_re.findall(r"ARGUS_[A-Z0-9_]+", joined))
    invented = sorted(doc_env - real_env)
    check(f"docs name only real ARGUS_* variables ({len(real_env)})",
          not invented, f"{invented} not read anywhere in argus/")

    # 4b. the residuals section states how many classes are capped for want
    #     of a verifier. That number lived only in prose and drifted from the
    #     matrix twice while classes came off the list, in both ARCHITECTURE
    #     and CHANGELOG, so `cap_reason` makes it derivable and this check
    #     holds the sentence to it.
    # "no"/"none" so the docs can state a count of ZERO explicitly rather
    # than by saying nothing - a deleted sentence must not read as agreement
    _WORDS = {"no": 0, "none": 0,
              "one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
              "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
    unimplemented = sorted(
        spec.vuln_class
        for spec in {s.vuln_class: s for s in proof.MATRIX.values()}.values()
        if spec.cap_reason == proof.CAP_UNIMPLEMENTED)
    stated = set()
    for text in texts.values():
        for word in _re.findall(
                r"(?i)\*\*([A-Za-z]+) class(?:es)? (?:are|is) capped at "
                r"`candidate`", text):
            if word.lower() in _WORDS:
                stated.add(_WORDS[word.lower()])
            elif word.isdigit():
                stated.add(int(word))
    check(f"docs state the capped count correctly ({len(unimplemented)}: "
          f"{', '.join(unimplemented)})",
          bool(stated) and stated == {len(unimplemented)},
          f"docs say {sorted(stated) or 'nothing'}, the matrix caps "
          f"{len(unimplemented)} for want of a verifier")
    # Which names in that paragraph are the capped ones cannot be read out of
    # prose - it also names the classes that CAME OFF the list, in the same
    # sentence. What is unambiguous, and is the risk worth covering, is the
    # other direction: a cap added to the matrix and never written down.
    capped_doc = "\n".join(texts.values())
    undocumented = sorted(k for k in unimplemented
                          if f"`{k}`" not in capped_doc)
    check("every capped class is named somewhere in the docs",
          not undocumented,
          f"{undocumented} capped for want of a verifier and named in no doc")
    # and the real-reason caps, which are a different promise to the reader
    real = sorted(spec.vuln_class
                  for spec in {s.vuln_class: s
                               for s in proof.MATRIX.values()}.values()
                  if spec.ceiling and spec.cap_reason != proof.CAP_UNIMPLEMENTED)
    missing_real = sorted(k for k in real if f"`{k}`" not in capped_doc)
    check(f"every real-reason cap is named too ({', '.join(real)})",
          not missing_real, f"{missing_real} capped and named in no doc")
    # This sentence IS parseable, unlike the other paragraph: the backticked
    # names come immediately before the claim. It listed `ppoll` as capped for
    # a real reason when ppoll is not capped at all.
    claimed_real = set()
    for text in texts.values():
        for head in _re.findall(
                r"(?i)\*\*((?:`[a-z]{3,12}`[^*]{0,40}){1,5})are capped for a "
                r"real reason", text):
            claimed_real |= set(_re.findall(r"`([a-z]{3,12})`", head))
    not_capped = sorted(n for n in claimed_real
                        if proof.spec_for(n) is not None
                        and not proof.spec_for(n).ceiling)
    check("the real-reason sentence names only capped classes",
          not not_capped,
          f"{not_capped} claimed capped for a real reason, but the matrix "
          f"does not cap them at all")

    # 4c. `docs/EXPERIMENTS.md` states how many classes cannot reach `proven`
    #     at all, and that number is the denominator of every recall figure in
    #     the evaluation. It said nine for a long time after it was three,
    #     because nothing counted it: the doc gate counted tools, classes and
    #     test totals, and not this.
    unreachable = sorted(
        spec.vuln_class
        for spec in {x.vuln_class: x for x in proof.MATRIX.values()}.values()
        if spec.ceiling or spec.verifier is proof.verify_refused)
    stated_unreachable = set()
    for text in texts.values():
        for word in _re.findall(
                r"(?i)\*\*([A-Za-z]+) class(?:es)? cannot reach `proven`",
                text):
            if word.lower() in _WORDS:
                stated_unreachable.add(_WORDS[word.lower()])
            elif word.isdigit():
                stated_unreachable.add(int(word))
    check(f"docs state the unreachable-class count correctly "
          f"({len(unreachable)}: {', '.join(unreachable)})",
          bool(stated_unreachable)
          and stated_unreachable == {len(unreachable)},
          f"docs say {sorted(stated_unreachable) or 'nothing'}, the matrix "
          f"puts {len(unreachable)} out of reach")
    missing_named = sorted(k for k in unreachable
                           if f"`{k}`" not in "\n".join(texts.values()))
    check("every unreachable class is named in the docs", not missing_named,
          f"{missing_named} cannot reach proven and is named in no doc")

    # 5. every proof class named in a doc exists, and every class the docs
    #    claim is refused really is
    classes = set(proof.classes())
    # Widened, and given a floor. This matched one literal form, `argus
    # proof <name>`, which across the whole gated doc set names exactly two
    # classes - `rce` and `sqli`. Reword those two usage examples to
    # `argus proof <class>` and `named_classes` is empty, `missing` is
    # empty, and the check reports PASS while validating nothing; from that
    # point a document could name a class the matrix does not have.
    #
    # It now also reads `load_skill("<name>")` and backtick-quoted names on
    # a line that mentions a class or a skill, and the floor is what makes
    # the widening honest: a check that can validate zero names is not a
    # check. Names are resolved through `spec_for`, so an ALIAS counts - the
    # docs name `cache-poisoning`, `info-disclosure`, `host-header` and
    # `deserialization`, every one of which resolves, and demanding the bare
    # class name would have been a wrong fix dressed as a strictness.
    named_classes = set(_re.findall(r"argus proof ([a-z][a-z0-9-]*)", joined))
    named_classes |= set(_re.findall(r'load_skill\(\s*"([a-z][a-z0-9-]*)"',
                                     joined))
    for line in joined.splitlines():
        if not _re.search(r"(?i)\bclass(?:es)?\b|\bskill\b", line):
            continue
        for token in _re.findall(r"`([a-z][a-z0-9-]{2,24})`", line):
            if proof.spec_for(token) is not None:
                named_classes.add(token)
    missing = sorted(c for c in named_classes
                     if c and proof.spec_for(c) is None)
    check(f"docs name only real proof classes "
          f"({len(named_classes)} named, {len(classes)} in the matrix)",
          not missing and len(named_classes) >= 10,
          f"{missing} named in a doc and absent from the matrix" if missing
          else (f"{len(named_classes)} resolved, none invented"
                if len(named_classes) >= 10 else
                f"only {len(named_classes)} class name(s) found in the gated "
                "docs - the patterns have stopped matching, so this check is "
                "validating almost nothing"))
    check("the matrix still refuses dos",
          proof.spec_for("dos") is not None
          and proof.spec_for("dos").verifier is proof.verify_refused)
    check("every proof class has a requirement sentence",
          all(proof.requirement_of(c) for c in classes))

    # 6. every test name a LIVE document cites is a test that exists.
    #
    #    `docs/VERIFICATION.md` is a table of claim -> mechanism -> the test
    #    that holds it, and that is the document a reviewer reads to check a
    #    claim rather than take it. Its whole value is the third column, so a
    #    renamed or deleted test silently unbacks a claim and nothing said
    #    so: this gate checked tools, subcommands, flags, proof classes,
    #    ARGUS_* variables and stated counts, and not the 82 test names in
    #    the one document whose purpose is to name them.
    #
    #    CHANGELOG.md is deliberately out of scope. It is a historical
    #    record, so an entry that says a test was deleted names it correctly
    #    by its old name, and failing on that would punish an accurate
    #    sentence.
    defined = set()
    for path in sorted((ROOT / "tests").glob("test_*.py")):
        defined |= set(_re.findall(r"(?m)^def (test_[A-Za-z0-9_]+)",
                                   path.read_text(encoding="utf-8")))
    defined |= set(_re.findall(r"(?m)^def (test_[A-Za-z0-9_]+)",
                               (ROOT / "selftest.py")
                               .read_text(encoding="utf-8")))
    modules = {p.name for p in (ROOT / "tests").glob("test_*.py")}
    unknown, cited_total = {}, 0
    for name in ("docs/VERIFICATION.md", "docs/ARCHITECTURE.md", "AGENTS.md"):
        text = texts.get(name)
        if not text:
            continue
        # an identifier wrapped across two lines inside its backticks is one
        # name, not a truncated one - join before matching
        flat = _re.sub(r"`([^`]*)`",
                       lambda m: "`" + _re.sub(r"\s*\n\s*", "",
                                               m.group(1)) + "`",
                       text, flags=_re.S)
        for ident, ext in _re.findall(r"`(test_[A-Za-z0-9_]+)(\.py)?", flat):
            cited_total += 1
            ok = (ident + ext) in modules if ext else ident in defined
            if not ok:
                unknown.setdefault(name, set()).add(ident + ext)
    check(f"live docs name only tests that exist ({cited_total} cited)",
          not unknown,
          "; ".join(f"{k}: {sorted(v)}" for k, v in unknown.items())
          + " - named in a live document and defined nowhere")
    # A regex that stops matching would make the check above pass forever on
    # nothing, and the claims table without its third column is just
    # assertions.
    # 7. nothing large or opaque is tracked in git.
    #
    #    The biggest tracked file is ~150 KB and the package is
    #    standard-library-only by design, so a megabyte of anything is a
    #    mistake - and the mistake is close at hand. This working tree holds
    #    a 19 MB `ghidra.zip` and two 4 MB binaries, untracked and NOT
    #    ignored, so one `git add -A` writes ~27 MB of binaries into the
    #    history, where removing them means rewriting it. This check does
    #    not decide what may be committed; it refuses the shapes that cannot
    #    be taken back. The file count is in the label so a run with no git
    #    (an sdist checkout) reads as "0 examined" rather than as agreement.
    _LIMIT = 1 << 20
    _OPAQUE = (".zip", ".tar", ".tgz", ".gz", ".bz2", ".xz", ".7z", ".rar",
               ".iso", ".dmg", ".exe", ".dll", ".so", ".bin", ".jar")
    tracked, oversized = [], []
    try:
        listing = _sub.run(["git", "ls-files", "-z"], cwd=ROOT,
                           capture_output=True, timeout=30)
        if listing.returncode == 0:
            tracked = [n for n in listing.stdout.decode(
                "utf-8", "replace").split("\0") if n]
    except (OSError, _sub.SubprocessError):
        tracked = []
    for name in tracked:
        fp = ROOT / name
        if not fp.is_file():
            continue
        if name.lower().endswith(_OPAQUE):
            oversized.append(f"{name} (opaque)")
        else:
            try:
                size = fp.stat().st_size
            except OSError:
                continue
            if size > _LIMIT:
                oversized.append(f"{name} ({size // 1024} KiB)")
    check(f"nothing large or opaque is tracked ({len(tracked)} examined)",
          not oversized,
          f"{sorted(oversized)[:6]} - an archive or a megabyte of binary in "
          "the history can only be removed by rewriting it")

    # 8. a methodology module that teaches a class names the tool that
    #    drives it.
    #
    #    `load_skill` puts these in front of the model when the signal points
    #    at a class, and INDEX.md says the module name resolves to a matrix
    #    class directly or through an alias - so the mapping is computable
    #    and the denominator is the class -> tool table, not whatever the
    #    module happens to mention. Ten of the twenty-four class modules
    #    named no tool of their class at all: an agent reading `ssrf.md` on
    #    an SSRF signal was taught the methodology and never told
    #    `probe_ssrf` exists. Nothing noticed, because the only check here
    #    was that a named tool is real - never that the right one is named.
    from argus.decide import CLASS_TOOL_CHAIN, PROBE_CLASS

    drivers: dict[str, set] = {}
    for tool, klass in PROBE_CLASS.items():
        drivers.setdefault(klass, set()).add(tool)
    for klass, chain in CLASS_TOOL_CHAIN.items():
        drivers.setdefault(klass, set()).update(chain)
    silent, module_count = [], 0
    for fp in sorted((ROOT / "argus" / "skills").glob("*.md")):
        if fp.name == "INDEX.md":
            continue
        spec = proof.spec_for(fp.stem)
        if spec is None:          # methodology only, by design
            continue
        module_count += 1
        wanted = drivers.get(spec.vuln_class, set())
        if not wanted:            # a class no tool drives, e.g. dos
            continue
        body = fp.read_text(encoding="utf-8")
        if not any(tool in body for tool in wanted):
            silent.append(f"{fp.name} ({spec.vuln_class}: "
                          f"{sorted(wanted)[0]})")
    check(f"every class module names its own tool ({module_count} modules)",
          not silent,
          f"{silent} - the module teaches the class and never names the tool "
          "that drives it, so the agent reading it does not learn the tool "
          "exists")

    # 8b. ...and the mirror: every gradeable class is TAUGHT by some module.
    #
    #     Check 8 reads module -> class, which is the direction you only
    #     change on purpose. The direction that rots is a class with no
    #     module: `load_skill` attached a proof requirement only when the
    #     module's STEM resolved, and five gradeable classes have no
    #     `<class>.md` - `enum`, `jwt`, `lockout`, `massassign` and
    #     `method`, taught by `auth-enum`, `auth-session` and `triage`. An
    #     agent loading the right module for any of them got the methodology
    #     and none of the requirement, which is the half that changes what
    #     it sends.
    #
    #     Coverage is derived the same way `load_skill` derives it - from
    #     the driving tools each module names - so the two cannot disagree.
    #     `dos` is exempt because it is refused by construction and has no
    #     methodology to teach.
    from argus.tools.analysis import _also_taught

    taught: set[str] = set()
    for fp in sorted((ROOT / "argus" / "skills").glob("*.md")):
        if fp.name == "INDEX.md":
            continue
        body = fp.read_text(encoding="utf-8")
        own = proof.spec_for(fp.stem)
        own_class = own.vuln_class if own else ""
        if own_class:
            taught.add(own_class)
        taught.update(_also_taught(body, own_class))
    gradeable = {k for k in proof.classes()
                 if proof.spec_for(k).verifier is not proof.verify_refused}
    untaught = sorted(gradeable - taught)
    check(f"every gradeable class is taught by a module "
          f"({len(taught)} taught, {len(gradeable)} gradeable)",
          not untaught and len(taught) >= len(gradeable),
          f"{untaught} can be proven and no methodology module teaches them, "
          "so `load_skill` has nothing to attach a requirement to"
          if untaught else f"{len(taught)} reachable, none orphaned")

    # 9. the Python range the package CLAIMS is the range CI proves.
    #
    #    `requires-python = ">=3.10"` is open-ended: pip installs on every
    #    version from the floor up, so each one is a support claim. The
    #    matrix tested 3.10-3.12 while the development interpreter was 3.14,
    #    which left 3.13 claimed by the metadata and tested by nobody - a
    #    claim exceeding its evidence, which is the one thing this gate
    #    exists to refuse. Two conditions make the claim checkable: the floor
    #    must be in the matrix, and the matrix must have no gap, so adding a
    #    new top version without the one below it fails here.
    wf = (ROOT / ".github" / "workflows" / "test.yml")
    pyproject = (ROOT / "pyproject.toml")
    if wf.is_file() and pyproject.is_file():
        wf_text = wf.read_text(encoding="utf-8")
        floor_m = _re.search(r'requires-python\s*=\s*">=\s*(\d+)\.(\d+)"',
                             pyproject.read_text(encoding="utf-8"))
        row = _re.search(r"(?m)^\s*python:\s*\[([^\]]*)\]", wf_text)
        versions = []
        if row:
            for part in _re.findall(r'"(\d+)\.(\d+)"', row.group(1)):
                versions.append((int(part[0]), int(part[1])))
        floor = ((int(floor_m.group(1)), int(floor_m.group(2)))
                 if floor_m else None)
        gaps = []
        if versions:
            lo, hi = min(versions), max(versions)
            if lo[0] == hi[0]:
                gaps = [f"3.{m}" for m in range(lo[1], hi[1] + 1)
                        if (lo[0], m) not in versions]
        check(f"CI proves the Python range the package claims "
              f"({len(versions)} tested)",
              bool(versions) and floor is not None
              and floor in versions and not gaps,
              (f"requires-python floor {floor} is not in the CI matrix "
               f"{sorted(versions)}" if floor and floor not in versions else
               f"the matrix skips {gaps}" if gaps else
               "no python matrix or no requires-python floor found - the "
               "support claim became uncheckable"))

    # 10. the reverse direction: every registered tool is named somewhere.
    #
    #     The check above asks that a tool named in a document is real. It
    #     never asked that a real tool is named, and two were not: the model
    #     could call `read_findings` and `list_exploits` while no document
    #     said they exist, so nobody reading the reference could learn to
    #     use them. One direction of a correspondence is half a check, and
    #     this gate has now been wrong that way about test tables, probe
    #     coverage, the document set and methodology modules.
    tool_doc_text = "\n".join(texts.values())
    unnamed = sorted(n for n in tool_names if n not in tool_doc_text)
    check(f"every registered tool is named in a document ({len(tool_names)})",
          not unnamed,
          f"{unnamed} can be called and no document says so")

    # 11. .env.example names every variable the code reads.
    #
    #     This is the file an operator copies to .env, so completeness is
    #     its whole purpose - and it named seven of the ten. The three
    #     absent ones were ARGUS_SEAL_KEY, ARGUS_MCP_CWD and
    #     ARGUS_EXPLOITS_CWD, all real-env-only switches, and the seal key
    #     is the one that matters: an operator setting up a keyed engagement
    #     learned nothing about it from the configuration file. The existing
    #     check ran the other way round - that a variable named in a
    #     document exists - which is the fifth time in this session that one
    #     direction of a correspondence turned out to be the whole check.
    env_example = texts.get(".env.example", "")
    read_vars = set()
    for fp in sorted((ROOT / "argus").rglob("*.py")):
        read_vars |= set(_ENV_READ_RE.findall(
            fp.read_text(encoding="utf-8")))
    unlisted = sorted(v for v in read_vars if v not in env_example)
    check(f"`.env.example` names every variable the code reads "
          f"({len(read_vars)} read)",
          bool(read_vars) and not unlisted,
          f"{unlisted} are read by argus/ and absent from the file an "
          "operator copies to configure it")

    # 12. the default model is priced and not deprecated.
    #
    #     `DEFAULT_MODEL` was `claude-sonnet-4-5`, deprecated and retiring
    #     2026-11-30 - a value that was right when written and that nothing
    #     checked. Every run without `--model` or `ARGUS_MODEL` pointed at a
    #     model that stops answering this month, and `.env.example` offered
    #     it as the example. A retirement date cannot be checked offline, so
    #     the table carries the deprecation as DATA - the same move as
    #     `cap_reason` in the proof matrix - and this refuses a default that
    #     is unpriced or marked deprecated. It also refuses a model named in
    #     a document that the table does not price, because an unpriced
    #     model reports no cost at all.
    from argus import models as _models
    from argus.config import DEFAULT_MODEL

    spec = _models.get(DEFAULT_MODEL)
    note = (getattr(spec, "note", "") or "") if spec else ""
    check(f"the default model is priced and current ({DEFAULT_MODEL})",
          spec is not None and "DEPRECATED" not in note.upper(),
          f"{DEFAULT_MODEL} is not in models.json - every run without "
          "--model would report no cost" if spec is None else
          f"{DEFAULT_MODEL}: {note}")
    priced = set(_models.keys()) if hasattr(_models, "keys") else set()
    if not priced:
        import json as _json
        priced = set(_json.loads(
            (ROOT / "argus" / "models.json").read_text(
                encoding="utf-8"))["models"])
    doc_models = set(_re.findall(r"`(claude-[a-z0-9-]+|gpt-[0-9.a-z-]+)`",
                                 "\n".join(texts.values())))
    unpriced = sorted(m for m in doc_models if m not in priced)
    check(f"docs name only models this build prices ({len(priced)} priced)",
          not unpriced,
          f"{unpriced} are named in a document and absent from models.json, "
          "so a run on one reports no cost")

    # 13. every import the shipped package makes is stdlib or a DECLARED
    #     dependency.
    #
    #     `AGENTS.md` says "No new runtime dependencies without strong
    #     cause" and `CLAUDE.md` says an engagement should not fail on a pip
    #     install. Both were prose. One `import requests` in a probe keeps
    #     the suite green on a developer machine that happens to have it,
    #     ships a wheel that cannot run, and surfaces mid-engagement - the
    #     worst possible moment for an import error.
    #
    #     The allowlist is derived from `pyproject.toml`, not hard-coded to
    #     `httpx`: declaring a dependency is a deliberate act that should
    #     pass, and importing one nobody declared is what must fail.
    import ast as _ast
    import sys as _sys

    declared = set()
    pyproject = (ROOT / "pyproject.toml")
    if pyproject.is_file():
        block = _re.search(r"(?s)^dependencies\s*=\s*\[(.*?)\]",
                           pyproject.read_text(encoding="utf-8"), _re.M)
        if block:
            for spec in _re.findall(r'"([^"]+)"', block.group(1)):
                declared.add(_re.split(r"[<>=!\[ ]", spec, 1)[0]
                             .strip().replace("-", "_").lower())
    ok_names = set(_sys.stdlib_module_names) | declared | {"argus"}
    undeclared: dict[str, set] = {}
    scanned = 0
    for fp in sorted((ROOT / "argus").rglob("*.py")):
        scanned += 1
        try:
            tree = _ast.parse(fp.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in _ast.walk(tree):
            names = []
            if isinstance(node, _ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            elif (isinstance(node, _ast.ImportFrom) and node.level == 0
                  and node.module):
                names = [node.module.split(".")[0]]
            for name in names:
                if name and name.lower() not in ok_names:
                    undeclared.setdefault(name, set()).add(
                        fp.relative_to(ROOT).as_posix())
    check(f"the package imports only stdlib and declared deps "
          f"({scanned} modules, declared: {sorted(declared) or 'none'})",
          bool(scanned) and not undeclared,
          "; ".join(f"{k} in {sorted(v)[:2]}" for k, v in undeclared.items())
          + " - undeclared, so `pip install -e .` does not install it and "
            "the failure lands mid-engagement")

    check("the claims table still names the tests that hold it",
          cited_total >= 50,
          f"only {cited_total} test names cited across the live docs - "
          "docs/VERIFICATION.md is a claim -> mechanism -> test table and "
          "the third column is the only thing that makes it checkable")


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
