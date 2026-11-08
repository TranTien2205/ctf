"""argus CLI: run an assessment, re-render a report, inspect a session."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import load_config
from .loop import AgentLoop
from .session import Session


def _add_run_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("target", help="Base URL of the in-scope target")
    p.add_argument("--scope", action="append",
                   help="Extra in-scope hosts (comma-separated ok); may repeat")
    p.add_argument("--exclude", action="append",
                   help="Path prefixes to never touch (e.g. /logout); may repeat")
    p.add_argument("--header", action="append",
                   help="'Name: value' applied to every request (e.g. auth cookie)")
    p.add_argument("--goal", help="Operator goal, e.g. 'focus on the /api surface'")
    p.add_argument("--model", help="Claude model id (default claude-sonnet-4-5)")
    p.add_argument("--api-key", help="Anthropic API key (else ANTHROPIC_API_KEY)")
    p.add_argument("--auth-token",
                   help="OAuth bearer token (Pro/Max; else ANTHROPIC_AUTH_TOKEN, "
                        "Claude Code or OpenCode credential store)")
    p.add_argument("--max-turns", type=int, default=80)
    p.add_argument("--max-requests", type=int, default=400)
    p.add_argument("--max-time", type=float, default=2400,
                   help="Wall-clock budget in seconds")
    p.add_argument("--rate", type=float, default=5.0, help="Requests/second cap")
    p.add_argument("--proxy",
                   help="Route target traffic through a proxy for inspection "
                        "(e.g. Burp/ZAP at http://127.0.0.1:8080)")
    p.add_argument("--session-dir", default="sessions")
    p.add_argument("--allow-private", action="store_true",
                   help="Permit private/loopback targets (auto-allowed if target is private)")
    p.add_argument("--tls-verify", action="store_true",
                   help="Verify TLS certificates (default off for labs/self-signed)")
    p.add_argument("--no-external", action="store_true",
                   help="Disable sqlmap/nuclei/nmap/ffuf/curl wrapper")
    p.add_argument("--llm-max-tokens", type=int, default=4096)
    p.add_argument("--mcp-config",
                   help="Path to mcp.json declaring MCP tool servers "
                        "(else ARGUS_MCP_CONFIG or ./mcp.json)")
    p.add_argument("--resume",
                   help="Session dir to continue: transcript, findings and "
                        "request ids carry over; evidence chain stays intact")
    p.add_argument("--quiet", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="argus", description="Argus - LLM agent for authorized web pentests")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run an autonomous assessment")
    _add_run_args(p_run)

    p_team = sub.add_parser(
        "team", help="run a lead-orchestrated team assessment (multi-agent)")
    _add_run_args(p_team)
    p_team.add_argument("--recon", type=int, default=1,
                        help="initial recon workers (default 1)")
    p_team.add_argument("--exploit", type=int, default=1,
                        help="initial exploit workers (default 1)")
    p_team.add_argument("--report-workers", type=int, default=0,
                        help="initial report workers (default 0)")
    p_team.add_argument("--max-workers", type=int, default=6,
                        help="cap on concurrently running workers (default 6)")

    p_rep = sub.add_parser("report", help="re-render report.md for a session dir")
    p_rep.add_argument("session_dir")

    p_find = sub.add_parser("findings", help="print findings of a session dir")
    p_find.add_argument("session_dir")
    p_find.add_argument("--json", action="store_true")

    p_skills = sub.add_parser("skills", help="list knowledge modules")
    p_skills.set_defaults(list_skills=True)

    p_sess = sub.add_parser("sessions", help="list past session dirs")
    p_sess.add_argument("--session-dir", default="sessions")

    p_cmp = sub.add_parser(
        "compare", help="compare two sessions' metrics side by side "
                        "(e.g. run vs team for the experiment chapter)")
    p_cmp.add_argument("dir_a")
    p_cmp.add_argument("dir_b")

    p_demo = sub.add_parser(
        "demo", help="offline scripted run against the bundled lab - "
                     "exercises the full pipeline with no API key")
    p_demo.add_argument("--session-dir", default="sessions")
    p_demo.add_argument("--team", action="store_true",
                        help="run the demo through the lead/worker pipeline")
    p_demo.add_argument("--quiet", action="store_true")

    args = parser.parse_args(argv)

    if args.cmd == "run":
        cfg = load_config(args)
        loop = AgentLoop(cfg, quiet=args.quiet)
        result = loop.run()
        print(json.dumps(result, indent=2))
        return 1 if result.get("error") else 0

    if args.cmd == "team":
        from .team.coordinator import TeamRun
        cfg = load_config(args)
        team = TeamRun(cfg, quiet=args.quiet,
                       n_recon=args.recon, n_exploit=args.exploit,
                       n_report=args.report_workers,
                       max_workers=args.max_workers)
        result = team.run()
        print(json.dumps(result, indent=2))
        return 1 if result.get("lead_error") else 0

    if args.cmd == "report":
        from .report.markdown import render_report
        sdir = Path(args.session_dir)
        session = _reopen(sdir)
        cfg = load_config(argparse.Namespace(
            target="http://x", header=[], scope=[], exclude=[], model=None,
            api_key=None, auth_token=None, max_turns=0, max_requests=0,
            max_time=0, rate=0,
            session_dir="sessions", allow_private=True, tls_verify=False,
            no_external=True, goal="", llm_max_tokens=0))
        cfg.model = session.dir.name
        path = render_report(session, cfg)
        print(path)
        return 0

    if args.cmd == "findings":
        fpath = Path(args.session_dir) / "findings.json"
        if not fpath.exists():
            print("[]" if args.json else "no findings.json in that session dir")
            return 1
        data = json.loads(fpath.read_text(encoding="utf-8"))
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            for f in data:
                print(f"[{f['severity'].upper():8}] {f['id']} {f['title']} ({f['url']})")
        return 0

    if args.cmd == "skills":
        sdir = Path(__file__).parent / "skills"
        for p in sorted(sdir.glob("*.md")):
            print(p.stem)
        return 0

    if args.cmd == "sessions":
        root = Path(args.session_dir)
        rows = []
        for d in sorted(root.iterdir()) if root.exists() else []:
            if not d.is_dir():
                continue
            row = {"dir": d.name}
            summ = d / "summary.json"
            if summ.exists():
                try:
                    s = json.loads(summ.read_text(encoding="utf-8"))
                    row.update(mode=s.get("mode", "single"),
                               findings=len(s.get("findings") or []),
                               requests=s.get("requests", "?"))
                except Exception:
                    pass
            rows.append(row)
        if not rows:
            print("no sessions yet")
            return 0
        for r in rows:
            print(f"{r['dir']}  {r.get('mode','?'):<6} "
                  f"findings={r.get('findings','?')} "
                  f"requests={r.get('requests','?')}")
        return 0

    if args.cmd == "compare":
        def _summ(d):
            p = Path(d) / "summary.json"
            if not p.exists():
                return {"dir": Path(d).name}
            s = json.loads(p.read_text(encoding="utf-8"))
            agents = s.get("agents") or {}
            if isinstance(agents, dict):
                agents = list(agents.values())
            return {
                "dir": Path(d).name, "mode": s.get("mode", "single"),
                "findings": len(s.get("findings") or []),
                "requests": s.get("requests", 0),
                "ttf": s.get("time_to_first_finding_s"),
                "coverage": len((s.get("coverage") or {}).get("endpoints") or []),
                "llm_calls": s.get("llm_calls", 0),
                "tokens": (s.get("llm_tokens") or {}),
                "workers": len(agents),
            }
        a, b = _summ(args.dir_a), _summ(args.dir_b)
        keys = [("mode", "mode"), ("findings", "findings"),
                ("requests", "requests"),
                ("ttf", "time_to_first_finding_s"),
                ("coverage", "endpoints_touched"),
                ("llm_calls", "llm_calls"), ("workers", "workers")]
        print(f"{'metric':<24} {'A':<32} {'B':<32}")
        print(f"{'':24} {a['dir']:<32} {b['dir']:<32}")
        for k, label in keys:
            print(f"{label:<24} {str(a.get(k)):<32} {str(b.get(k)):<32}")
        for who, s in (("A", a), ("B", b)):
            t = s.get("tokens") or {}
            print(f"tokens({who}){'':18} in={t.get('in',0)} out={t.get('out',0)}")
        return 0

    if args.cmd == "demo":
        return _demo(args)

    return 2


def _demo(args) -> int:
    """Offline demo for presentations/defense: spins up the lab and runs a
    scripted agent sequence through the real loop - scope guard, probes,
    evidence gate, findings and report all live. No API key needed."""
    import sys as _sys
    import threading
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "lab"))
    import vulnapp  # noqa: E402

    from .llm import ScriptedClient
    from .config import Config

    srv = vulnapp.make_server(0)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    def _t(i, name, **kw):
        return {"id": f"d{i}", "name": name, "type": "tool_use", "input": kw}

    # Request numbering is deterministic: sqli=4 (r1-r4), reflection=1 (r5),
    # idor=3 (r6-r8), xfh=1 (r9).
    script = [
        {"text": "Baseline-diffed probes first: /item looks injectable.",
         "tool_calls": [_t(1, "probe_sqli", url=base + "/item?id=1",
                          param="id")]},
        {"tool_calls": [_t(2, "record_finding",
                         title="SQL injection in /item id parameter",
                         severity="high", category="sqli",
                         url=base + "/item?id=1",
                         evidence_ids=["r2"],
                         evidence_excerpt="sqlite3.OperationalError",
                         description="The quote probe produces a raw sqlite "
                                     "error - unsanitized input reaches the "
                                     "query.",
                         remediation="Use parameterized queries.",
                         cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")],
         "text": "Error channel confirms SQLi - recording with verbatim "
                 "evidence."},
        {"tool_calls": [_t(3, "probe_reflection",
                         url=base + "/search?q=x", param="q")],
         "text": "Now the reflected-parameter family."},
        {"tool_calls": [_t(4, "record_finding",
                         title="Reflected XSS in /search q parameter",
                         severity="medium", category="xss",
                         url=base + "/search?q=x",
                         evidence_ids=["r5"],
                         evidence_excerpt="<>'\"&=/",
                         description="Canary chars < > \" ' reflect "
                                     "unescaped in html context.",
                         remediation="Output-encode by context; add CSP.",
                         cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N")],
         "text": "Reflected with unescaped special chars - XSS lead."},
        {"tool_calls": [_t(5, "probe_idor", url=base + "/api/user/2")],
         "text": "Object-level authorization next."},
        {"tool_calls": [_t(6, "record_finding",
                         title="IDOR: /api/user/<id> serves any user object",
                         severity="high", category="idor",
                         url=base + "/api/user/2",
                         evidence_ids=["r7"],
                         evidence_excerpt="\"username\"",
                         description="Neighboring ids return other users' "
                                     "objects with no authorization check.",
                         remediation="Enforce per-object ownership checks.",
                         cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")],
         "text": "Neighbor id returns a different principal - IDOR."},
        {"tool_calls": [_t(7, "probe_xfh", url=base + "/reset")]},
        {"tool_calls": [_t(8, "finish",
                         summary="Demo run: SQLi + XSS + IDOR verified with "
                                 "verbatim evidence; host-header reflection "
                                 "left as a lead for manual follow-up.")]},
    ]
    cfg = Config(target=base, allow_private=True,
                 session_dir=Path(args.session_dir),
                 model="scripted-demo", max_turns=12, rate_rps=0)
    if args.team:
        result = _demo_team(cfg, base, _t, args, ScriptedClient)
    else:
        result = AgentLoop(cfg, llm=ScriptedClient(script),
                           quiet=args.quiet).run()
    srv.shutdown()
    print("\n=== demo complete ===")
    fpath = Path(result["session_dir"]) / "findings.json"
    if fpath.exists():
        for f in json.loads(fpath.read_text(encoding="utf-8")):
            print(f"  [{f['severity'].upper()}] {f['title']}")
    print(f"  findings={result['findings']}  requests={result['requests']}")
    print(f"  report: {result['report']}")
    return 0


def _demo_team(cfg, base, _t, args, ScriptedClient):
    """Same scripted assessment through the real lead/worker pipeline:
    lead seeds the lead queue, a recon worker maps the surface, an exploit
    worker pulls the leads and verifies each one. Findings cite evidence by
    excerpt, resolved to the recorded exchange automatically - deterministic
    despite workers sharing one transcript."""
    from .team.coordinator import TeamRun

    scripts = {
        "lead": [
            {"text": "Seeding the pipeline with the three most promising "
                     "surfaces.",
             "tool_calls": [
                 _t("l1", "emit_lead", kind="param", url=base + "/item?id=1",
                    params=["id"], note="sql-error surface on id"),
                 _t("l2", "emit_lead", kind="param", url=base + "/search?q=x",
                    params=["q"], note="reflected parameter"),
                 _t("l3", "emit_lead", kind="endpoint",
                    url=base + "/api/user/2", note="enumerable object ids")]},
            {"text": "Leads queued; workers drain while I close out.",
             "tool_calls": [_t("l4", "finish_engagement",
                              summary="Team demo: recon mapped the surface, "
                                      "exploit verified SQLi, XSS and IDOR "
                                      "with verbatim evidence.")]},
        ],
        "recon": [
            {"text": "Mapping stack and surface for the exploit workers.",
             "tool_calls": [
                 _t("r1", "fingerprint", url=base),
                 _t("r2", "crawl", url=base, depth=1, max_pages=10)]},
            {"tool_calls": [_t("r3", "note",
                              text="Python http.server lab; /item, /search, "
                                   "/api/user exposed."),
                            _t("r4", "finish",
                               summary="Surface mapped; leads seeded.")]},
        ],
        "exploit": [
            {"text": "Pulling queued surface leads.",
             "tool_calls": [_t("e1", "pull_leads", max_n=5)]},
            {"text": "Confirming the injectable id parameter.",
             "tool_calls": [_t("e2", "probe_sqli", url=base + "/item?id=1",
                              param="id")]},
            {"tool_calls": [_t("e3", "record_finding",
                              title="SQL injection in /item id parameter",
                              severity="high", category="sqli",
                              url=base + "/item?id=1",
                              evidence_excerpt="sqlite3.OperationalError",
                              description="Quote probe yields a raw sqlite "
                                          "error - unsanitized input reaches "
                                          "the query.",
                              remediation="Use parameterized queries.")]},
            {"tool_calls": [_t("e4", "probe_reflection",
                              url=base + "/search?q=x", param="q")]},
            {"tool_calls": [_t("e5", "record_finding",
                              title="Reflected XSS in /search q parameter",
                              severity="medium", category="xss",
                              url=base + "/search?q=x",
                              evidence_excerpt="<>'\"&=/",
                              description="Canary chars reflect unescaped "
                                          "in html context.",
                              remediation="Output-encode by context; "
                                          "add CSP.")]},
            {"tool_calls": [_t("e6", "probe_idor",
                              url=base + "/api/user/2")]},
            {"tool_calls": [_t("e7", "record_finding",
                              title="IDOR: /api/user/<id> serves any user",
                              severity="high", category="idor",
                              url=base + "/api/user/2",
                              evidence_excerpt="\"username\"",
                              description="Neighboring ids return other "
                                          "users' objects, no authz check.",
                              remediation="Enforce per-object ownership "
                                          "checks.")]},
            {"tool_calls": [_t("e8", "finish",
                              summary="3/3 leads verified with verbatim "
                                      "evidence.")]},
        ],
    }

    def _factory(role: str, _name: str):
        return ScriptedClient(scripts.get(role, []))

    cfg.max_turns = 15
    return TeamRun(cfg, llm_factory=_factory, quiet=args.quiet,
                   n_recon=1, n_exploit=1, n_report=0).run()


def _reopen(sdir: Path) -> Session:
    """Rebuild a Session view over an existing session directory."""
    sess = Session.__new__(Session)
    sess.dir = sdir
    sess.id = sdir.name
    sess.started = 0.0
    sess._seq = 0
    sess._transcript = {}
    tpath = sdir / "transcript.jsonl"
    if tpath.exists():
        for line in tpath.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            entry = json.loads(line)
            sess._transcript[entry["id"]] = entry
            sess._seq = max(sess._seq, int(entry["id"][1:]) if entry["id"][1:].isdigit() else 0)
    fpath = sdir / "findings.json"
    sess.findings = json.loads(fpath.read_text(encoding="utf-8")) if fpath.exists() else []
    return sess


if __name__ == "__main__":
    sys.exit(main())
