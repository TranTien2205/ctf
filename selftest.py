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
    check("ffuf guard confines wordlists",
          bool(_ffuf_arg_check(ctx, ["-w", "/etc/passwd:FUZZ", "-u", base])))
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
    check("ssrf probe sees file-scheme content",
          any(h["marker"] for h in out["results"]
              if h["name"].startswith("file")))
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
    check("upload probe serves active file", "upload candidate" in out["verdict"])
    out = probes.probe_race(ctx, base + "/redeem", n=8)
    check("race probe multi-redeems", "race candidate" in out["verdict"])
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
          "cl.te desync candidate" in out["verdict"])
    out = probes.probe_smuggle(ctx, base + "/desync-cl")
    check("smuggle probe sees te.cl desync",
          "te.cl desync candidate" in out["verdict"])
    out = probes.probe_smuggle(ctx, base + "/desync-obf")
    check("smuggle probe sees obfuscated-te desync",
          "obfuscated TE" in out["verdict"])
    out = probes.probe_smuggle(ctx, base + "/desync-none")
    check("smuggle probe clean on agreed framing",
          "no desync signal" in out["verdict"])
    out = probes.probe_crlf(ctx, base + "/redirect?next=/", "next")
    check("crlf probe injects header",
          "crlf injection candidate" in out["verdict"])
    out = probes.probe_disclosure(ctx, base)
    check("disclosure probe finds exposed paths",
          {h["path"] for h in out["exposed"]} >= {"/.git/HEAD", "/.env", "/debug"})
    out = probes.probe_websocket(ctx, base + "/ws")
    check("websocket probe confirms upgrade", "confirmed" in out["verdict"])

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
    check("lead queue dedups",
          q.push(Lead(kind="endpoint", url=base + "/a")) is True
          and q.push(Lead(kind="endpoint", url=base + "/a")) is False)
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
    out = teamtools.run_exploit(ctx, "lab-auth-bypass", "http://x.invalid/")
    check("exploit runner scope-checks target", "error" in out)

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
