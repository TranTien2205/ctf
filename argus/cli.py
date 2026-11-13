"""argus CLI: run an assessment, re-render a report, inspect a session."""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .config import Config, load_config
from .loop import AgentLoop
from .session import Session


def _add_run_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("target", help="Base URL of the in-scope target")
    p.add_argument("--role", default=None,
                   help="pick the model by what the task needs rather than by "
                        "name (planner|breadth|depth|judge|writer); "
                        "`argus models` lists them. --model wins over this")
    p.add_argument("--policy", default="cheap", choices=["cheap", "strong"],
                   help="with --role: the cheapest model the table says can "
                        "do the job, or the strongest (default cheap)")
    p.add_argument("--role-models", action="store_true",
                   help="team mode only: give each role the model the table "
                        "lists for its job (lead=planner, recon=breadth, "
                        "exploit=depth, report=writer) under --policy. A pick "
                        "whose credential is not set falls back to --model")
    p.add_argument("--seal-key", default=None,
                   help="HMAC key (or a path to a file holding one) for the "
                        "transcript chain. Unkeyed, the chain proves the file "
                        "was not edited; keyed, only a holder of the key can "
                        "produce a chain that verifies. Also ARGUS_SEAL_KEY")
    p.add_argument("--require-proof", action="store_true",
                   help="refuse findings whose evidence does not meet the "
                        "proof requirement for their class (default: record "
                        "them graded as candidate/unproven)")
    p.add_argument("--scope", action="append",
                   help="Extra in-scope hosts (comma-separated ok); may repeat")
    p.add_argument("--exclude", action="append",
                   help="Path prefixes to never touch (e.g. /logout); may repeat")
    p.add_argument("--header-file",
                   help="File with one 'Name: value' header per line "
                        "(e.g. a Burp copy); blank lines and # comments "
                        "skipped; framing headers (Host, Content-Length, "
                        "Transfer-Encoding, Connection) dropped - the wire "
                        "computes them from the scoped URL")
    p.add_argument("--header", action="append",
                   help="'Name: value' applied to every request (e.g. auth cookie)")
    p.add_argument("--secret", action="append",
                   help="A credential value (password, session token, API "
                        "key, >=4 chars) to redact verbatim from every "
                        "persisted artifact - transcript bodies, event "
                        "output, notes, logs. May repeat.")
    p.add_argument("--goal", help="Operator goal, e.g. 'focus on the /api surface'")
    p.add_argument("--operator",
                   help="Tester/org attribution recorded in meta.json and "
                        "rendered in the report header")
    p.add_argument("--model",
                   help="model id (default claude-sonnet-5-5). `argus models` "
                        "lists the table; a name it does not know is sent to "
                        "Anthropic")
    p.add_argument("--api-key", help="Anthropic API key (else ANTHROPIC_API_KEY)")
    p.add_argument("--auth-token",
                   help="OAuth bearer token (Pro/Max; else ANTHROPIC_AUTH_TOKEN, "
                        "Claude Code or OpenCode credential store)")
    p.add_argument("--max-turns", type=int, default=80,
                   help="LLM turn budget (0 = no cap)")
    p.add_argument("--max-requests", type=int, default=400,
                   help="HTTP request budget per agent (0 = no cap)")
    p.add_argument("--max-time", type=float, default=2400,
                   help="Wall-clock budget in seconds (0 = no cap)")
    p.add_argument("--rate", type=float, default=5.0,
                   help="Requests/second cap (0 = no cap)")
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
                        "(else ARGUS_MCP_CONFIG; a ./mcp.json in cwd is "
                        "ignored unless ARGUS_MCP_CWD=1)")
    p.add_argument("--tools",
                   help="Comma-separated tool allowlist (run mode only), "
                        "e.g. 'http_request,probe_sqli,record_finding'. "
                        "Shrinks the tool-schema payload per LLM call - "
                        "needed on token-constrained auth (OAuth extra "
                        "usage). 'finish' is always included.")
    p.add_argument("--resume",
                   help="Session dir to continue: transcript, findings and "
                        "request ids carry over; evidence chain stays intact")
    p.add_argument("--quiet", action="store_true")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="argus", description="Argus - LLM agent for authorized web pentests")
    from . import __version__
    parser.add_argument("--version", action="version",
                        version=f"argus {__version__}")
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

    p_serve = sub.add_parser(
        "mcp-serve",
        help="serve argus's tools to an MCP host over stdio - the LLM that "
             "drives the assessment lives outside, the guards stay here")
    _add_run_args(p_serve)

    p_rep = sub.add_parser("report", help="re-render report.md for a session dir")
    p_rep.add_argument("session_dir")
    p_rep.add_argument("--seal-key", default=None,
                       help="the key the run was sealed with, if any - a "
                            "re-render re-seals, and chaining unkeyed over a "
                            "keyed transcript would break it")

    p_find = sub.add_parser("findings", help="print findings of a session dir")
    p_find.add_argument("session_dir")
    p_find.add_argument("--json", action="store_true")

    p_skills = sub.add_parser(
        "skills", help="list knowledge modules, or print one with "
                       "'skills <name>'")
    p_skills.add_argument("name", nargs="?", default=None)
    p_skills.set_defaults(list_skills=True)

    p_check = sub.add_parser(
        "check", help="preflight: verify auth/credentials work before a run")
    p_check.add_argument("--api-key"); p_check.add_argument("--auth-token")
    p_check.add_argument("--model")
    p_check.add_argument("--json", action="store_true",
                         help="machine-readable verdict (ok/degraded/error)")

    p_judge = sub.add_parser(
        "judge", help="have a model from a different family read the evidence "
                      "behind each finding. It can dispute or lower, never "
                      "promote - the grade belongs to the proof matrix")
    p_judge.add_argument("session_dir")
    p_judge.add_argument("--judge-model", default=None,
                         help="override the table's pick; refused if it is "
                              "the same family as the model that ran")
    p_judge.add_argument("--policy", default="strong",
                         choices=["cheap", "strong"])
    p_judge.add_argument("--only", default="",
                         help="comma-separated finding ids (default: all)")
    p_judge.add_argument("--seal-key", default=None)
    p_judge.add_argument("--json", action="store_true")
    p_judge.add_argument("--dry-run", action="store_true",
                         help="print the case file a judge would be sent and "
                              "make no call")

    p_next = sub.add_parser(
        "next", help="what the recorded evidence says to do next, computed "
                     "from a session directory rather than from the "
                     "conversation")
    p_next.add_argument("session", help="path to a session directory")
    p_next.add_argument("--json", action="store_true")

    p_models = sub.add_parser(
        "models", help="the model table: provider, price, and which roles "
                       "each model is listed for")
    p_models.add_argument("--json", action="store_true")

    p_proof = sub.add_parser(
        "proof", help="print the proof requirement for a bug class, or list "
                      "all classes with 'proof'")
    p_proof.add_argument("vuln_class", nargs="?", default=None)
    p_proof.add_argument("--json", action="store_true")

    p_sess = sub.add_parser("sessions", help="list past session dirs")
    p_sess.add_argument("--session-dir", default="sessions")
    p_sess.add_argument("--json", action="store_true",
                        help="machine-readable listing for experiment scripts")

    p_ver = sub.add_parser(
        "verify", help="verify a session's transcript hash chain "
                       "(tamper-evidence check)")
    p_ver.add_argument("session_dir")
    p_ver.add_argument("--seal-key", default=None,
                       help="the key the run was sealed with, if any")
    p_ver.add_argument("--json", action="store_true",
                       help="print the raw verification result as JSON")

    p_diff = sub.add_parser(
        "diff", help="findings-level retest diff between two sessions: "
                     "FIXED / STILL PRESENT / NEW (match = bug class + "
                     "endpoint + params)")
    p_diff.add_argument("before")
    p_diff.add_argument("after")
    p_diff.add_argument("--json", action="store_true")

    p_cmp = sub.add_parser(
        "compare", help="compare sessions' metrics side by side "
                        "(e.g. run vs team for the experiment chapter)")
    p_cmp.add_argument("dirs", nargs="+",
                       help="two or more session dirs")
    p_cmp.add_argument("--by-arm", action="store_true",
                       help="group the trials by configuration and report the "
                            "median of each metric per arm, with N and the "
                            "spread. The arm is the parent directory with a "
                            "trailing -<trial> stripped, which is the layout "
                            "docs/EXPERIMENTS.md lays out")
    p_cmp.add_argument("--csv", action="store_true",
                       help="print metrics as CSV rows for spreadsheets")

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
        _preflight_target(cfg)
        allowed = _parse_tools(getattr(args, "tools", "") or "")
        loop = AgentLoop(cfg, quiet=args.quiet, allowed=allowed)
        result = loop.run()
        print(json.dumps(result, indent=2))
        return 1 if result.get("error") else 0

    if args.cmd == "mcp-serve":
        from .mcpserver import serve
        cfg = load_config(args)
        # no _preflight_target: the host may connect before the target is up,
        # and a server that exits on a cold target is a server the host cannot
        # keep registered
        return serve(cfg, allowed=_parse_tools(getattr(args, "tools", "") or ""))

    if args.cmd == "team":
        from .team.coordinator import TeamRun
        if getattr(args, "tools", ""):
            raise SystemExit("--tools applies to 'run' only - team workers "
                             "already carry role-card tool subsets")
        cfg = load_config(args)
        _preflight_target(cfg)
        for flag, val in (("--recon", args.recon),
                          ("--exploit", args.exploit),
                          ("--report-workers", args.report_workers),
                          ("--max-workers", args.max_workers)):
            if val < 0:
                raise SystemExit(f"{flag} must be >= 0")
        if args.max_workers < 1:
            # zero workers = no probe tools, no record_finding anywhere -
            # the lead alone structurally cannot produce a finding
            raise SystemExit("--max-workers must be >= 1")
        if args.exploit <= 0:
            # the lead card holds no record_finding - unless it spawns an
            # exploit worker itself, the run structurally records nothing
            print("warning: --exploit 0 - findings require the lead to "
                  "spawn an exploit worker; it may only map surface",
                  file=sys.stderr)
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
        if not (sdir / "transcript.jsonl").exists():
            # refuse: an empty dir would render a sealed, verifying
            # "session" out of nothing - the seal must only ever anchor
            # artifacts a real run produced
            print(f"no transcript.jsonl in {sdir} - not a session dir")
            return 1
        from .config import _seal_key
        session = _reopen(sdir, _seal_key(args))
        if not session._transcript:
            # a transcript with zero entries means the run died at init -
            # rendering + sealing a zero-evidence report fabricates an
            # engagement that never happened
            print(f"{sdir} has an empty transcript - nothing to report")
            return 1
        # bare Config suffices - the renderer only reads cfg.model, and
        # resolving auth here could refresh OAuth creds as a side effect of
        # a read-only command
        cfg = Config(target="http://x")
        try:
            meta = json.loads((sdir / "meta.json").read_text(
                encoding="utf-8"))
            cfg.model = meta.get("model") or cfg.model
        except Exception:
            pass
        # a re-render must not silently carry tampered claims: findings.json
        # is not chained, so re-validate every finding's evidence against
        # the transcript before trusting it - and warn when the transcript
        # itself fails the chain check
        from .session import findings_bad, verify_transcript
        v = verify_transcript(sdir)
        if not v.get("chained") or v.get("tail_truncated") \
                or v.get("bad_lines"):
            print("warning: transcript chain check failed - report may "
                  "reflect an edited/truncated transcript "
                  "(run 'argus verify' for detail)", file=sys.stderr)
        if v.get("artifact_mismatch"):
            print(f"warning: {v['artifact_mismatch']} edited since the "
                  "run was sealed - constraints/findings may not reflect "
                  "the original run (run 'argus verify')", file=sys.stderr)
        bad = findings_bad(session._transcript, session.findings)
        if bad:
            print(f"warning: findings {bad} fail evidence re-validation - "
                  "excluded from this report (run 'argus verify' for detail)",
                  file=sys.stderr)
            session.findings = [f for f in session.findings
                                if isinstance(f, dict)
                                and f.get("id") not in bad]
        # A stored grade stronger than its evidence is the same kind of
        # tampering, and the re-render would have re-sealed it: `argus report`
        # computed nothing about grades, so an inflated claim came out of the
        # other side with a fresh, valid digest over it. Correct it to what
        # the evidence supports and say so.
        from .session import findings_overgraded
        inflated = findings_overgraded(session._transcript, session.findings)
        if inflated:
            by_id = {row["id"]: row for row in inflated}
            for f in session.findings:
                row = by_id.get(f.get("id")) if isinstance(f, dict) else None
                if not row:
                    continue
                print(f"warning: {row['id']} claims grade "
                      f"'{row['claimed']}' but its evidence supports "
                      f"'{row['evidence_supports']}' - corrected in this "
                      "report (run 'argus verify' for detail)",
                      file=sys.stderr)
                if row["evidence_supports"] in ("proven", "candidate",
                                                "unproven", "refused"):
                    f["grade"] = row["evidence_supports"]
                    f["grade_corrected_from"] = row["claimed"]
        # the agent's summary lives in summary.json; without it the
        # re-rendered report says "_No agent summary was recorded._"
        carried = ""
        try:
            prev = json.loads((sdir / "summary.json").read_text(
                encoding="utf-8"))
            if isinstance(prev, dict):
                carried = str(prev.get("agent_summary") or "")
        except (ValueError, OSError):
            carried = ""
        path = render_report(session, cfg, summary=carried)
        # a re-render is a new attested artifact state: seal again so the
        # delivered report.* files are digest-anchored too
        try:
            session.seal_artifacts()
        except OSError as exc:
            print(f"warning: could not seal artifacts ({exc}) - this "
                  "render is not digest-anchored", file=sys.stderr)
        print(path)
        return 0

    if args.cmd == "findings":
        fpath = Path(args.session_dir) / "findings.json"
        if not fpath.exists():
            print("[]" if args.json else "no findings.json in that session dir")
            return 1
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
        except ValueError:
            print(f"{fpath} is not valid JSON - session dir corrupt")
            return 1
        if not isinstance(data, list):
            print(f"{fpath} is not a findings list - session dir corrupt")
            return 1
        # findings.json is not chained - flag any claim whose evidence
        # fails re-validation instead of presenting it as trustworthy
        from .session import findings_bad, verify_transcript
        _v = verify_transcript(Path(args.session_dir))
        if _v.get("artifact_mismatch"):
            print(f"warning: {_v['artifact_mismatch']} edited since the "
                  "run was sealed (run 'argus verify')", file=sys.stderr)
        bad = set(findings_bad(_reopen(Path(args.session_dir))._transcript,
                               data))
        if bad:
            print(f"warning: findings {sorted(bad)} fail evidence "
                  "re-validation - do not trust (run 'argus verify')",
                  file=sys.stderr)
        if args.json:
            print(json.dumps(data, indent=2, ensure_ascii=False))
        else:
            # context line: which target + build produced these claims
            _m = {}
            try:
                _r = json.loads((Path(args.session_dir) / "meta.json")
                                .read_text(encoding="utf-8"))
                _m = _r if isinstance(_r, dict) else {}
            except Exception:
                pass
            _ctx = f" target={_m['target']}" if _m.get("target") else ""
            _ctx += f" argus={_m['argus_version']}" \
                if _m.get("argus_version") else ""
            if _ctx:
                print(f"--- {Path(args.session_dir).name}{_ctx} ---")
            for f in data:
                if not isinstance(f, dict):
                    print("[?       ] ? <malformed entry> UNVERIFIED")
                    continue
                cvss = f" [{f['cvss']}]" if f.get("cvss") else ""
                cwe = f" {f['cwe']}" if f.get("cwe") else ""
                ow = f" <{f['owasp']}>" if f.get("owasp") else ""
                flag = " UNVERIFIED" if f.get("id") in bad else ""
                sev = str(f.get("severity") or "?").upper()
                grade = f" {str(f.get('grade') or '').upper()}" \
                    if f.get("grade") else ""
                print(f"[{sev:8}]{grade} {f.get('id', '?')} {f.get('title', '?')}"
                      f" ({f.get('url', '')}){cwe}{ow}{cvss}{flag}")
        return 0

    if args.cmd == "judge":
        return _cmd_judge(args)

    if args.cmd == "next":
        from . import decide as decide_mod
        action = decide_mod.next_action(args.session)
        print(json.dumps(action.to_dict(), indent=2, ensure_ascii=False)
              if args.json else action.render())
        return 0

    if args.cmd == "models":
        from . import models as models_mod
        table = models_mod.known()
        if args.json:
            print(json.dumps(
                {"version": models_mod.table_version(),
                 "roles": models_mod.roles(),
                 "models": {k: {"provider": m.provider, "display": m.display,
                                "api_base": m.api_base,
                                "api_key_env": m.api_key_env,
                                "context_window": m.context_window,
                                "usd_per_mtok_in": m.usd_per_mtok_in,
                                "usd_per_mtok_out": m.usd_per_mtok_out,
                                "roles": m.roles,
                                "credential_present": bool(m.credential())}
                           for k, m in table.items()}}, indent=2))
            return 0
        print(f"model table v{models_mod.table_version()} - prices are USD per "
              "million tokens as published, and they move: a cost in a report "
              "traces to a line here\n")
        print(f"{'model':20} {'provider':10} {'in':>7} {'out':>7} {'cred':5} roles")
        for key, m in sorted(table.items()):
            cred = "yes" if m.credential() else "-"
            print(f"{key:20} {m.provider:10} {m.usd_per_mtok_in:7.2f} "
                  f"{m.usd_per_mtok_out:7.2f} {cred:5} {','.join(m.roles)}")
        print("\nroles:")
        for role, why in models_mod.roles().items():
            cheap = models_mod.for_role(role, "cheap")
            strong = models_mod.for_role(role, "strong")
            print(f"  {role:9} cheap={cheap.key if cheap else '-':20} "
                  f"strong={strong.key if strong else '-'}")
            print(f"            {why}")
        return 0

    if args.cmd == "proof":
        from . import proof as proof_mod
        if not args.vuln_class:
            if args.json:
                print(json.dumps({c: proof_mod.requirement_of(c)
                                  for c in proof_mod.classes()}, indent=2))
                return 0
            print(f"{len(proof_mod.classes())} classes in the proof matrix "
                  "- `argus proof <class>` for one:\n")
            for name in proof_mod.classes():
                print(f"  {name:14} {proof_mod.requirement_of(name)[:90]}")
            return 0
        spec = proof_mod.spec_for(args.vuln_class)
        if spec is None:
            print(f"no proof requirement for {args.vuln_class!r}. "
                  f"Classes: {', '.join(proof_mod.classes())}", file=sys.stderr)
            return 2
        if args.json:
            print(json.dumps({
                "vuln_class": spec.vuln_class, "requirement": spec.requirement,
                "required": list(spec.required), "veto": list(spec.veto),
                "floor": list(spec.floor), "aliases": list(spec.aliases),
                "notes": spec.notes, "refusal": spec.refusal}, indent=2))
            return 0
        print(f"{spec.vuln_class} - proof requirement\n")
        print(f"  {spec.requirement}\n")
        if spec.refusal:
            print(f"  REFUSED: {spec.refusal}")
            return 0
        print("  checks that must pass:")
        for name in spec.required:
            print(f"    - {name}")
        if spec.floor:
            print("  without this one, nothing above 'unproven' is available:")
            for name in spec.floor:
                print(f"    - {name}")
        if spec.veto:
            print("  disqualifies the evidence entirely:")
            for name in spec.veto:
                print(f"    - {name}")
        if spec.ceiling:
            # an operator reading this needs to know `proven` is unreachable
            # BEFORE spending an engagement trying to reach it
            from .proof import CAP_UNIMPLEMENTED
            print(f"\n  CAPPED AT '{spec.ceiling}': this system will not "
                  f"grade this class higher.")
            if spec.cap_reason == CAP_UNIMPLEMENTED:
                print("    Reason: the verifier is unwritten. The transcript "
                      "already records what it\n            would need, so "
                      "this is labour, not a limit.")
            elif spec.cap_reason:
                print(f"    Reason: {spec.cap_reason}. Not something more "
                      f"work here would fix.")
        if spec.verifier.__name__ == "verify_refused":
            print(f"\n  REFUSED: {spec.refusal or spec.requirement}")
        if spec.notes:
            print(f"\n  {spec.notes}")
        if spec.aliases:
            print(f"\n  also accepted as: {', '.join(spec.aliases)}")
        return 0

    if args.cmd == "skills":
        sdir = Path(__file__).parent / "skills"
        if args.name:
            import re as _re
            safe = _re.sub(r"[^a-z0-9_-]", "", args.name.lower())
            f = sdir / f"{safe}.md"
            if f.exists():
                print(f.read_text(encoding="utf-8"), end="")
                return 0
            print(f"no skill '{args.name}' - "
                  f"available: {', '.join(p.stem for p in sorted(sdir.glob('*.md')) if p.stem != 'INDEX')}")
            return 1
        for p in sorted(sdir.glob("*.md")):
            if p.stem != "INDEX":
                print(p.stem)
        return 0

    if args.cmd == "sessions":
        root = Path(args.session_dir)
        rows = []
        for d in sorted(root.iterdir()) if root.is_dir() else []:
            if not d.is_dir():
                continue
            row = {"dir": d.name}
            summ = d / "summary.json"
            if summ.exists():
                try:
                    s = json.loads(summ.read_text(encoding="utf-8"))
                    row.update(mode=s.get("mode", "single"),
                               findings=len(s.get("findings") or []),
                               requests=s.get("requests", "?"),
                               duration=s.get("duration_s"),
                               sealed=bool(s.get("sealed")),
                               version=s.get("argus_version") or "?")
                except Exception:
                    pass
            rows.append(row)
        if args.json:
            print(json.dumps(rows, indent=2, ensure_ascii=False))
            return 0
        if not rows:
            print("no sessions yet")
            return 0
        for r in rows:
            dur = f"{r['duration']:.0f}s" if isinstance(
                r.get("duration"), (int, float)) else "?"
            seal = " sealed" if r.get("sealed") else ""
            print(f"{r['dir']}  {r.get('mode','?'):<6} "
                  f"findings={r.get('findings','?')} "
                  f"requests={r.get('requests','?')} dur={dur} "
                  f"v{r.get('version','?')}{seal}")
        return 0

    if args.cmd == "verify":
        from .config import _seal_key
        from .session import verify_transcript
        res = verify_transcript(Path(args.session_dir), _seal_key(args))
        # provenance: which build wrote this evidence - matters when the
        # verifier's rules differ from the producer's
        try:
            _m = json.loads((Path(args.session_dir) / "meta.json")
                            .read_text(encoding="utf-8"))
            if isinstance(_m, dict):
                if _m.get("argus_version"):
                    res["produced_by"] = _m["argus_version"]
                if _m.get("resumed_by"):
                    res["resumed_by"] = _m["resumed_by"]
        except Exception:
            pass
        if args.json:
            # machine-readable verdict for CI: ok mirrors the exit code
            res["ok"] = not (res.get("error") or not res.get("chained")
                             or res.get("bad_lines")
                             or res.get("tail_truncated")
                             or res.get("anchor_missing")
                             or res.get("findings_bad")
                             or res.get("findings_overgraded")
                             or res.get("key_required")
                             or res.get("artifact_mismatch"))
            print(json.dumps(res, indent=2, ensure_ascii=False))
            return 0 if res["ok"] else 1
        if res.get("error"):
            print(res["error"])
            return 1
        if res.get("key_required"):
            print("UNVERIFIABLE: this run was sealed with a key. Pass "
                  "--seal-key (or set ARGUS_SEAL_KEY) - verifying it unkeyed "
                  "would report every line as tampered")
            return 1
        if not res["chained"]:
            print("transcript predates hash chaining - cannot verify")
            return 1
        if res["bad_lines"]:
            print(f"TAMPERED: chain mismatch at lines {res['bad_lines']} "
                  f"({res['entries']} chained entries checked)")
            return 1
        if res.get("tail_truncated"):
            print("MISMATCH: transcript tail does not reach the chain head "
                  "recorded in summary.json - tail entries were removed, "
                  "or the session continued after its last report")
            return 1
        if res.get("anchor_missing"):
            print("UNVERIFIABLE: summary.json carries no "
                  "transcript_chain_head - either this session predates "
                  "anchoring, or the anchor was deleted (which defeats "
                  "tail-truncation detection)")
            return 1
        if res.get("findings_bad"):
            print(f"TAMPERED: findings {res['findings_bad']} no longer "
                  "verify - evidence ids missing from the transcript or "
                  "excerpt not verbatim")
            return 1
        if res.get("findings_overgraded"):
            for row in res["findings_overgraded"]:
                print(f"TAMPERED: {row['id']} claims grade "
                      f"'{row['claimed']}' but its cited evidence supports "
                      f"'{row['evidence_supports']}'"
                      + (f" - unmet: {', '.join(row['missing'])}"
                         if row.get("missing") else ""))
            return 1
        if res.get("artifact_mismatch"):
            print(f"TAMPERED: {res['artifact_mismatch']} edited since the "
                  "run was sealed - sha256 differs from the digest "
                  "recorded in the transcript")
            return 1
        anchored = " anchored to summary.json" if res.get("head_anchor") \
            else ""
        fchk = (f", {res['findings_checked']} findings re-validated"
                if res.get("findings_checked") else "")
        sealed = ", artifacts sealed" if res.get("sealed") \
            else " (unsealed: predates artifact digests - only transcript " \
                 "and findings integrity verified)"
        prod = ""
        if res.get("produced_by"):
            prod = f" [produced by argus {res['produced_by']}"
            prod += f", resumed by {res['resumed_by']}]" \
                if res.get("resumed_by") else "]"
        print(f"OK: {res['entries']} chained entries verified{anchored}"
              f"{fchk}{sealed}{prod}")
        return 0

    if args.cmd == "check":
        from .config import resolve_auth, api_base_url, DEFAULT_MODEL
        from .llm import ClaudeClient
        key, tok = resolve_auth(args)
        src = ("api-key" if key else "oauth (Claude Code/OpenCode)"
               if tok else None)
        _js = getattr(args, "json", False)

        def _emit(rc: int, **kw) -> int:
            if _js:
                print(json.dumps({"ok": rc == 0, "degraded": rc == 2,
                                  "source": src, **kw},
                                 indent=2, ensure_ascii=False))
            return rc

        if not src:
            if _js:
                return _emit(1, error="no credentials")
            print("no credentials found - set ANTHROPIC_API_KEY or sign in "
                  "to Claude Code")
            return 1
        model = getattr(args, "model", None) or DEFAULT_MODEL
        # same endpoint a real run would hit: ANTHROPIC_BASE_URL gateway
        # included, or 'check' would certify a path 'run' never uses
        c = ClaudeClient(api_key=key or "", auth_token=tok or "",
                         api_base=api_base_url(), model=model, max_tokens=8)
        try:
            c.chat(messages=[{"role": "user", "content": "say OK"}],
                   tools=[], system="one word")
        except Exception as exc:
            if _js:
                return _emit(1, error=str(exc))
            print(f"auth failed via {src}: {exc}")
            return 1
        # a bare ping is not the real failure mode - metered OAuth tiers
        # accept it yet reject the ~30KB tool schema a run actually sends
        from .tools.registry import TOOL_SCHEMAS, BOARD_TOOLS
        surface = [s for s in TOOL_SCHEMAS if s["name"] not in BOARD_TOOLS]
        try:
            c.chat(messages=[{"role": "user", "content": "say OK"}],
                   tools=surface, system="one word")
            if _js:
                return _emit(0, model=model, tools=len(surface))
            print(f"auth ok via {src}, model={model}, "
                  f"full tool surface ({len(surface)} tools) accepted")
            return 0
        except Exception as exc:
            if _js:
                return _emit(2, model=model, tools=len(surface),
                             error=str(exc))
            print(f"auth ok via {src}, model={model} - but the full tool "
                  f"surface ({len(surface)} tools) was REJECTED:\n  {exc}\n"
                  f"  -> this credential caps request size (metered OAuth "
                  f"extra-usage). Use 'argus run --tools <list>' or "
                  f"'argus team' (role-card subsets are smaller).")
            return 2  # degraded: auth works, but a default run would die

    if args.cmd == "diff":
        from .session import _finding_key
        import urllib.parse as _up

        def _dkey(f):
            # retests usually run on a fresh instance (new port) - match on
            # host + path + params + class, ignoring the port
            # the canonical class, not the author's spelling: keying on raw
            # category made one unfixed finding report as both FIXED and NEW
            # when the two runs spelled the class differently
            cat, _netloc, path, params = _finding_key(
                f.get("vuln_class") or f.get("category"), f.get("url"))
            u = str(f.get("url") or "")
            try:
                host = _up.urlparse(
                    u if "://" in u else "http://" + u).hostname
            except ValueError:
                host = None  # tampered url like http://[bad
            return (cat, (host or "").lower(), path, params)

        def _load(d):
            fp = Path(d) / "findings.json"
            if not fp.exists():
                raise SystemExit(f"no findings.json in {d}")
            try:
                rows = json.loads(fp.read_text(encoding="utf-8"))
            except ValueError:
                raise SystemExit(f"{fp} is not valid JSON")
            if not isinstance(rows, list):
                raise SystemExit(f"{fp} is not a findings list")
            return {_dkey(f): f for f in rows if isinstance(f, dict)}
        before, after = _load(args.before), _load(args.after)
        # a diff across DIFFERENT base hosts is meaningless by
        # construction - every finding reads as fixed+new. Retest diffs
        # are deliberately port-insensitive, but a host mismatch is
        # operator error, not a retest.
        def _meta(d):
            try:
                m = json.loads((Path(d) / "meta.json")
                               .read_text(encoding="utf-8"))
                return m if isinstance(m, dict) else {}
            except Exception:
                return {}
        mb, ma = _meta(args.before), _meta(args.after)
        hb = _up.urlparse(str(mb.get("target") or "")).hostname
        ha = _up.urlparse(str(ma.get("target") or "")).hostname
        if hb and ha and hb.lower() != ha.lower():
            print(f"warning: targets differ ({hb} vs {ha}) - a diff "
                  "across hosts reads every finding as fixed+new; "
                  "compare retests on the same host", file=sys.stderr)
        # a diff over tampered findings is misleading - flag sessions whose
        # stored claims fail evidence re-validation (same check as
        # `findings`/`report`)
        from .session import findings_bad
        for label, d in (("before", args.before), ("after", args.after)):
            try:
                bad = findings_bad(
                    _reopen(Path(d))._transcript,
                    json.loads((Path(d) / "findings.json")
                               .read_text(encoding="utf-8")))
            except Exception:
                bad = []
            if bad:
                print(f"warning: {label} session has findings {bad} that "
                      "fail evidence re-validation - diff may be "
                      "misleading", file=sys.stderr)
        fixed = [before[k] for k in sorted(set(before) - set(after))]
        still = [(before[k], after[k])
                 for k in sorted(set(before) & set(after))]
        new = [after[k] for k in sorted(set(after) - set(before))]
        if args.json:
            print(json.dumps({
                # provenance so a JSON diff is self-documenting, like
                # the compare table's target/version rows
                "before": {"dir": Path(args.before).name,
                           "target": mb.get("target"),
                           "argus_version": mb.get("argus_version")},
                "after": {"dir": Path(args.after).name,
                          "target": ma.get("target"),
                          "argus_version": ma.get("argus_version")},
                "fixed": fixed, "new": new,
                "still_present": [
                    {"id_before": b.get("id"), "id_after": a.get("id"),
                     "title": a.get("title"), "category": a.get("category"),
                     "url": a.get("url"),
                     "severity_before": b.get("severity"),
                     "severity_after": a.get("severity")}
                    for b, a in still],
            }, indent=2, ensure_ascii=False))
            return 0
        print(f"--- {Path(args.before).name} -> {Path(args.after).name} ---")
        for f in fixed:
            print(f"[FIXED ] {f.get('id')} {f.get('title')} "
                  f"({f.get('severity')})")
        for b, a in still:
            drift = (f" severity {b.get('severity')}->{a.get('severity')}"
                     if b.get("severity") != a.get("severity") else "")
            print(f"[STILL ] {b.get('id')}->{a.get('id')} {a.get('title')}"
                  f" ({a.get('severity')}){drift}")
        for f in new:
            print(f"[NEW   ] {f.get('id')} {f.get('title')} "
                  f"({f.get('severity')})")
        print(f"{len(fixed)} fixed, {len(still)} still present, "
              f"{len(new)} new")
        return 0

    if args.cmd == "compare":
        import urllib.parse as _up

        def _host_of(d):
            try:
                m = json.loads((Path(d) / "meta.json")
                               .read_text(encoding="utf-8"))
                t = m.get("target") if isinstance(m, dict) else None
                return (_up.urlparse(str(t or "")).hostname or "").lower()
            except Exception:
                return ""

        def _g(s, grade):
            g = s.get("grades")
            if isinstance(g, dict):
                try:
                    return int(g.get(grade, 0) or 0)
                except (TypeError, ValueError):
                    return 0
            # a session rendered before grading existed: count from the rows
            rows = s.get("findings")
            if not isinstance(rows, list):
                return 0
            return sum(1 for f in rows
                       if isinstance(f, dict) and f.get("grade") == grade)

        def _summ(d):
            p = Path(d) / "summary.json"
            if not p.exists():
                return {"dir": Path(d).name}
            try:
                s = json.loads(p.read_text(encoding="utf-8"))
            except ValueError:
                s = {}
            if not isinstance(s, dict):
                s = {}
            agents = s.get("agents")
            if isinstance(agents, dict):
                agents = list(agents.values())
            if not isinstance(agents, list):
                agents = []
            _cov = s.get("coverage")
            _eps = _cov.get("endpoints") if isinstance(_cov, dict) else None
            _tok = s.get("llm_tokens")
            return {
                "dir": Path(d).name, "mode": s.get("mode", "single"),
                "findings": len(s.get("findings"))
                            if isinstance(s.get("findings"), list) else 0,
                # The grade split, because a total alone invites a
                # configuration to win by recording more leads: EXPERIMENTS
                # makes the proven count the primary measure, and this is the
                # tool it tells the reader to use for it.
                "proven": _g(s, "proven"),
                "candidate": _g(s, "candidate"),
                "unproven": _g(s, "unproven"),
                "requests": s.get("requests", 0),
                "ttf": s.get("time_to_first_finding_s"),
                "duration_s": s.get("duration_s"),
                "coverage": len(_eps) if isinstance(_eps, list) else 0,
                "llm_calls": s.get("llm_calls", 0),
                "tokens": _tok if isinstance(_tok, dict) else {},
                "cost": s.get("llm_cost")
                        if isinstance(s.get("llm_cost"), dict) else {},
                "workers": len(agents),
                "version": s.get("argus_version") or "",
                "host": _host_of(d),
            }
        if getattr(args, "by_arm", False):
            return _compare_by_arm(args.dirs, _summ, _host_of,
                                   csv=bool(args.csv))
        if len(args.dirs) < 2:
            print("compare needs at least two session dirs")
            return 2
        # A/B comparisons assume the same target - different hosts make
        # the metric deltas meaningless, so flag it like `diff` does
        hosts = {_host_of(d) for d in args.dirs} - {""}
        if len(hosts) > 1:
            print(f"warning: targets differ ({', '.join(sorted(hosts))}) "
                  "- metrics only compare like-for-like on the same "
                  "target", file=sys.stderr)
        sums = [_summ(d) for d in args.dirs]
        # metrics produced by different argus builds are not like-for-like
        # either - probe counts and detection logic change between versions
        versions = {s["version"] for s in sums
                    if isinstance(s.get("version"), str)} - {""}
        if len(versions) > 1:
            print(f"warning: argus versions differ "
                  f"({', '.join(sorted(versions))}) - metrics only "
                  "compare like-for-like on the same build",
                  file=sys.stderr)
        if args.csv:
            # grade columns sit with `findings` because they decompose it;
            # the context columns stay appended last so existing positional
            # parsers keep working
            hdr = ("session,mode,findings,proven,candidate,unproven,"
                   "requests,ttf_s,duration_s,"
                   "endpoints,llm_calls,workers,tokens_in,tokens_out,"
                   "cache_read,cache_write,target_host,argus_version")
            print(hdr)
            for s in sums:
                t = s.get("tokens") or {}
                print(f"{s['dir']},{s.get('mode','?')},{s.get('findings','?')},"
                      f"{s.get('proven',0)},{s.get('candidate',0)},"
                      f"{s.get('unproven',0)},"
                      f"{s.get('requests','?')},{s.get('ttf') or ''},"
                      f"{s.get('duration_s') or ''},"
                      f"{s.get('coverage','?')},{s.get('llm_calls',0)},"
                      f"{s.get('workers',0)},{t.get('in',0)},{t.get('out',0)},"
                      f"{t.get('cache_read',0)},{t.get('cache_write',0)},"
                      f"{s.get('host','')},{s.get('version','')}")
            return 0
        keys = [("host", "target_host"), ("version", "argus_version"),
                ("mode", "mode"), ("findings", "findings"),
                ("proven", "proven"), ("candidate", "candidate"),
                ("unproven", "unproven"),
                ("requests", "requests"),
                ("ttf", "time_to_first_finding_s"),
                ("duration_s", "duration_s"),
                ("coverage", "endpoints_touched"),
                ("llm_calls", "llm_calls"), ("workers", "workers"),
                ("tokens", "tokens_in_out"), ("cache", "cache_read_write")]
        labels = [f"S{i + 1}" for i in range(len(sums))]
        w = max(24, max(len(s['dir']) for s in sums) + 2)
        print(f"{'metric':<24}" + "".join(f"{l:<{w}}" for l in labels))
        print(f"{'':24}" + "".join(f"{s['dir']:<{w}}" for s in sums))
        for k, label in keys:
            def _v(s, k=k):
                t = s.get("tokens") or {}
                if k == "tokens":
                    return f"{t.get('in',0)}/{t.get('out',0)}"
                if k == "cache":
                    return f"{t.get('cache_read',0)}/{t.get('cache_write',0)}"
                return str(s.get(k))
            print(f"{label:<24}" + "".join(f"{_v(s):<{w}}" for s in sums))
        return 0

    if args.cmd == "demo":
        return _demo(args)

    return 2


def _parse_tools(raw: str):
    """--tools allowlist -> frozenset for AgentLoop(allowed=...); None for
    the default full surface. Validates names up front - a typo'd tool
    silently absent for 80 turns is a wasted run."""
    names = {t.strip() for t in raw.split(",") if t.strip()}
    if not names:
        return None
    from .tools.registry import TOOL_SCHEMAS, BOARD_TOOLS
    valid = {s["name"] for s in TOOL_SCHEMAS} - BOARD_TOOLS
    bad = names - valid
    if bad:
        raise SystemExit(
            f"--tools: unknown tool(s) {sorted(bad)}\n"
            f"valid: {sorted(valid)}")
    names.add("finish")  # a run without finish() can only end on budgets
    return frozenset(names)


def _preflight_target(cfg) -> None:
    """Fail fast on a target the scope guard would reject anyway —
    before a session dir is created or an API call is burned."""
    from urllib.parse import urlparse
    from .scope import ScopeGuard
    try:
        u = urlparse(cfg.target or "")
    except ValueError:
        u = urlparse("")
    if u.scheme not in ("http", "https") or not u.hostname:
        raise SystemExit(
            f"invalid target {cfg.target!r}: expected http(s)://host[/path] "
            f"(you typed {cfg.target!r})")
    try:
        ScopeGuard(
            cfg.target, extra_hosts=cfg.scope_hosts,
            exclude_paths=cfg.exclude_paths,
            allow_private=cfg.allow_private).check(cfg.target)
    except Exception as exc:
        raise SystemExit(f"target rejected by scope guard: {exc}")


def _demo_scan(messages: list, key: str):
    """The newest tool_result carrying `key`, searching back through the whole
    conversation - the forge event is several turns behind the request that
    used its token."""
    for msg in reversed(messages):
        blocks = msg.get("content")
        if not isinstance(blocks, list):
            continue
        for block in reversed(blocks):
            if not isinstance(block, dict) or block.get("type") != "tool_result":
                continue
            try:
                out = json.loads(block.get("content") or "{}")
            except ValueError:
                continue
            result = out.get("result") if isinstance(out, dict) else None
            if isinstance(result, dict) and result.get(key):
                return result[key]
    return None


def _demo_last(messages: list) -> dict:
    """The most recent tool_result payload, as the model sees it.

    Both demo arms thread request ids through this: a scripted turn reads the
    previous result the same way Claude does, so the citations are built the
    way a real run builds them rather than from hard-coded request numbers.
    """
    for msg in reversed(messages):
        blocks = msg.get("content")
        if not isinstance(blocks, list):
            continue
        for block in reversed(blocks):
            if isinstance(block, dict) and block.get("type") == "tool_result":
                try:
                    out = json.loads(block.get("content") or "{}")
                except ValueError:
                    return {}
                return out.get("result", out) if isinstance(out, dict) else {}
    return {}


def _demo(args) -> int:
    """Offline demo for presentations/defense: spins up the lab and runs a
    scripted agent sequence through the real loop - scope guard, probes,
    evidence gate, findings and report all live. No API key needed."""
    import threading
    from .lab import vulnapp  # packaged, so demo works from a wheel too

    from .llm import ScriptedClient
    from .config import Config

    srv = vulnapp.make_server(0)
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    threading.Thread(target=srv.serve_forever, daemon=True).start()

    # The lab JWT embeds a live iat, so the token/forged strings must be
    # captured at demo setup and embedded literally into the script. This
    # setup fetch is outside the transcript on purpose - it is scripting,
    # not assessment.
    import urllib.request as _urlreq
    from .tools.analysis import jwt_forge as _jwt_forge
    _tok = json.loads(_urlreq.urlopen(
        base + "/token?user=alice", timeout=5).read())["token"]
    _forged = _jwt_forge(None, _tok, '{"user":"admin","role":"admin"}',
                         secret="secret123")["resigned"]

    def _t(i, name, **kw):
        return {"id": f"d{i}", "name": name, "type": "tool_use", "input": kw}

    _last = _demo_last

    # Ids are threaded out of each probe result, the way a real agent threads
    # them - every probe returns the request_ids it spent. The demo used to
    # omit evidence_ids and let the recorder resolve them from the excerpt,
    # which is how its "forged admin token accepted" finding came to cite
    # `GET /api/user/1`: an earlier response contained the same bytes.
    def _sqli_finding(messages):
        out = _last(messages)
        ids = out.get("request_ids") or {}
        extract = out.get("extract") or {}
        cited = [i for i in (ids.get("quote"), extract.get("request_id")) if i]
        return {"text": "Error channel named the engine; the bounded UNION read "
                        "returned rows. Both go in the citation - the class "
                        "needs the engine AND the data.",
                "tool_calls": [_t(2, "record_finding",
                    title="SQL injection in /item id parameter",
                    severity="critical", category="sqli",
                    url=base + "/item?id=1", evidence_ids=cited,
                    evidence_excerpt="admin - $s3cr3t-admin-pw",
                    description="id is interpolated into the query string. The "
                                "quote probe returns a raw sqlite error; a "
                                "UNION SELECT limited to five rows returns "
                                "credentials from the users table.",
                    remediation="Use parameterized queries.",
                    cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")]}

    def _rce_finding(messages):
        out = _last(messages)
        rid = out.get("proof_request_id")
        row = next((r for r in out.get("results") or []
                    if r.get("request_id") == rid and r.get("identity")), None)
        return {"text": "The host parameter reaches a shell: the identity line "
                        "came back with the probe nonce.",
                "tool_calls": [_t(4, "record_finding",
                    title="OS command injection in /ping host parameter",
                    severity="critical", category="rce",
                    url=base + "/ping?host=127.0.0.1",
                    evidence_ids=[rid] if rid else [],
                    evidence_excerpt=(row or {}).get("identity") or "uid=",
                    description="host is concatenated into a shell command. "
                                "`id; echo <nonce>` returns the server's own "
                                "identity line and the nonce, so the output is "
                                "computed by the target and not reflected.",
                    remediation="Never pass request data to a shell; exec with "
                                "an argv list and validate the host as an "
                                "address.",
                    cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")]}

    def _idor_finding(messages):
        out = _last(messages)
        other = next((r for r in out.get("results") or []
                      if r.get("accessible") and "admin" in (r.get("excerpt") or "")),
                     None)
        cited = [i for i in (out.get("base_id"),
                             (other or {}).get("request_id")) if i]
        return {"text": "Two object ids, two principals, one of them not mine.",
                "tool_calls": [_t(7, "record_finding",
                    title="IDOR: /api/user/<id> serves any user object",
                    severity="high", category="idor",
                    url=base + "/api/user/2", evidence_ids=cited,
                    evidence_excerpt='"username": "admin"',
                    description="Object ids are not checked against the caller. "
                                "Reading id 2 returns alice; reading id 1 "
                                "returns the admin record, with no credential "
                                "distinguishing the two requests.",
                    remediation="Enforce per-object ownership checks.",
                    cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")]}

    def _jwt_finding(messages):
        # the forged request is two turns back, the rejected control is last
        ids = []
        for msg in reversed(messages):
            blocks = msg.get("content")
            if not isinstance(blocks, list):
                continue
            for block in reversed(blocks):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    try:
                        out = json.loads(block.get("content") or "{}")
                    except ValueError:
                        continue
                    rid = (out.get("result") or {}).get("request_id") \
                        if isinstance(out.get("result"), dict) else None
                    if rid:
                        ids.append(rid)
            if len(ids) >= 2:
                break
        mint = _demo_scan(messages, "event_id")
        cited = ids[:2] + ([mint] if mint else [])
        return {"text": "Forged token accepted, deliberately invalid token "
                        "rejected - and the forge event is cited too, because "
                        "a working auth check looks the same on the wire.",
                "tool_calls": [_t(12, "record_finding",
                    title="JWT weak secret: forged admin token accepted",
                    severity="critical", category="jwt",
                    url=base + "/api/me", evidence_ids=cited,
                    evidence_excerpt='"role": "admin"',
                    description="The session JWT verifies against the "
                                "dictionary secret 'secret123'. A token forged "
                                "offline with role=admin is accepted and its "
                                "claims echoed back; the same request with a "
                                "broken signature is refused with 401, so the "
                                "endpoint does verify - against a guessable "
                                "key.",
                    remediation="Rotate to a high-entropy secret; prefer "
                                "asymmetric signing.",
                    cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")]}

    script = [
        {"text": "Baseline-diffed probes first: /item looks injectable, and "
                 "the class needs the engine named plus a row from a table.",
         "tool_calls": [_t(1, "probe_sqli", url=base + "/item?id=1",
                           param="id", union_cols=6, extract_table="users",
                           extract_columns="username,password")]},
        _sqli_finding,
        {"text": "A diagnostic endpoint takes a host - probe for command "
                 "OUTPUT, not for a delay.",
         "tool_calls": [_t(3, "probe_cmdi", url=base + "/ping?host=127.0.0.1",
                           param="host")]},
        _rce_finding,
        {"text": "Now the reflected-parameter family.",
         "tool_calls": [_t(5, "probe_reflection",
                           url=base + "/search?q=x", param="q")]},
        {"tool_calls": [_t(6, "record_finding",
                         title="Reflected XSS in /search q parameter",
                         severity="medium", category="xss",
                         url=base + "/search?q=x",
                         evidence_excerpt="<>'\"&=/",
                         description="Canary chars < > \" ' reflect unescaped "
                                     "in an html context. Execution is not "
                                     "shown here - this engagement had no "
                                     "browser, so the class stays a candidate.",
                         remediation="Output-encode by context; add CSP.",
                         cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N")],
         "text": "Unescaped reflection. Recording it as what it is: a "
                 "candidate, because nothing here executed it."},
        {"tool_calls": [_t(6, "probe_idor", url=base + "/api/user/2")],
         "text": "Object-level authorization next."},
        _idor_finding,
        {"tool_calls": [_t(8, "probe_disclosure", url=base)],
         "text": "Sensitive-artifact sweep before finishing."},
        {"tool_calls": [_t(9, "record_finding",
                         title="Exposed /.env and /.git/HEAD at web root",
                         severity="medium", category="info-disclosure",
                         url=base + "/.env",
                         evidence_excerpt="SECRET_KEY=lab-secret-0123",
                         description="Sensitive paths are served publicly - "
                                     "credentials and source-control "
                                     "metadata leak to anyone.",
                         remediation="Deny dotfile/VCS paths at the web "
                                     "server; rotate exposed secrets.",
                         cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")],
         "text": "Exposed secrets on the web root - recording."},
        {"tool_calls": [_t(10, "jwt_decode", token=_tok)],
         "text": "The session token itself is the next surface."},
        {"tool_calls": [_t(11, "jwt_forge", token=_tok,
                           claims='{"user":"admin","role":"admin"}',
                           secret="secret123")],
         "text": "Weak HMAC secret recovered offline - forge an admin token, "
                 "then send a deliberately broken one as the control."},
        {"tool_calls": [_t(12, "http_request", method="GET",
                           url=base + "/api/me",
                           headers={"Authorization": f"Bearer {_forged}"})]},
        {"tool_calls": [_t(13, "http_request", method="GET",
                           url=base + "/api/me",
                           headers={"Authorization":
                                    f"Bearer {_forged[:-4]}AAAA"})],
         "text": "The control: same request, signature broken by four bytes."},
        _jwt_finding,
        {"tool_calls": [_t(14, "probe_xfh", url=base + "/reset")]},
        {"tool_calls": [_t(15, "finish",
                         summary="Demo run. Proven: SQL injection (engine "
                                 "named plus five rows from users), OS command "
                                 "injection (identity line with the probe "
                                 "nonce), IDOR across two principals, exposed "
                                 "secrets, and a forged JWT accepted against a "
                                 "rejected control. Candidate: reflected XSS - "
                                 "unescaped, but no browser executed it. "
                                 "Host-header reflection left as a lead.")]},
    ]
    cfg = Config(target=base, allow_private=True,
                 session_dir=Path(args.session_dir),
                 model="scripted-demo", max_turns=16, rate_rps=0)
    if args.team:
        result = _demo_team(cfg, base, _t, args, ScriptedClient,
                            tok=_tok, forged=_forged)
    else:
        result = AgentLoop(cfg, llm=ScriptedClient(script),
                           quiet=args.quiet).run()
    srv.shutdown()
    print("\n=== demo complete ===")
    fpath = Path(result["session_dir"]) / "findings.json"
    if fpath.exists():
        try:
            _flist = json.loads(fpath.read_text(encoding="utf-8"))
        except ValueError:
            _flist = []
        for f in _flist if isinstance(_flist, list) else []:
            if isinstance(f, dict):
                sev = str(f.get("severity") or "?").upper()
                grade = f" ({f['grade']})" if f.get("grade") else ""
                print(f"  [{sev}]{grade} {f.get('title', '?')}")
    print(f"  findings={result['findings']}  requests={result['requests']}")
    print(f"  report: {result['report']}")
    html_path = Path(result['report']).with_suffix('.html')
    if html_path.exists():
        print(f"  html:   {html_path}")
    sarif_path = Path(result['report']).with_suffix('.sarif')
    if sarif_path.exists():
        print(f"  sarif:  {sarif_path}")
    return 0


def _demo_team(cfg, base, _t, args, ScriptedClient,
               tok: str = "", forged: str = ""):
    """Same scripted assessment through the real lead/worker pipeline:
    lead seeds the lead queue, a recon worker maps the surface, an exploit
    worker pulls the leads and verifies each one. Findings cite evidence by
    excerpt, resolved to the recorded exchange automatically - deterministic
    despite workers sharing one transcript."""
    from .team.coordinator import TeamRun

    # Same threading as the single-agent demo: every probe returns the
    # request_ids it spent, and the citation is built from them. The team arm
    # has to earn the same grades, or the run-vs-team comparison is comparing
    # two different standards of evidence.
    def _team_sqli_finding(messages):
        out = _demo_last(messages)
        ids = out.get("request_ids") or {}
        extract = out.get("extract") or {}
        cited = [i for i in (ids.get("quote"), extract.get("request_id")) if i]
        return {"tool_calls": [_t("e3", "record_finding",
            title="SQL injection in /item id parameter", severity="critical",
            category="sqli", url=base + "/item?id=1", evidence_ids=cited,
            evidence_excerpt="admin - $s3cr3t-admin-pw",
            description="id is interpolated into the query; a UNION read "
                        "limited to five rows returns users.username and "
                        "users.password.",
            remediation="Use parameterized queries.",
            cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")]}

    def _team_rce_finding(messages):
        out = _demo_last(messages)
        rid = out.get("proof_request_id")
        row = next((r for r in out.get("results") or []
                    if r.get("request_id") == rid and r.get("identity")), None)
        return {"tool_calls": [_t("e4b", "record_finding",
            title="OS command injection in /ping host parameter",
            severity="critical", category="rce",
            url=base + "/ping?host=127.0.0.1",
            evidence_ids=[rid] if rid else [],
            evidence_excerpt=(row or {}).get("identity") or "uid=",
            description="`id; echo <nonce>` returns the server's identity "
                        "line and the nonce - computed by the target.",
            remediation="Exec with an argv list; validate the host.",
            cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")]}

    def _team_idor_finding(messages):
        out = _demo_last(messages)
        other = next((r for r in out.get("results") or []
                      if r.get("accessible")
                      and "admin" in (r.get("excerpt") or "")), None)
        cited = [i for i in (out.get("base_id"),
                             (other or {}).get("request_id")) if i]
        return {"tool_calls": [_t("e7", "record_finding",
            title="IDOR: /api/user/<id> serves any user",
            severity="high", category="idor", url=base + "/api/user/2",
            evidence_ids=cited, evidence_excerpt='"username": "admin"',
            description="Reading id 2 returns alice, reading id 1 returns the "
                        "admin record, with no credential telling the two "
                        "requests apart.",
            remediation="Enforce per-object ownership checks.",
            cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")]}

    def _team_jwt_finding(messages):
        ids = []
        for msg in reversed(messages):
            blocks = msg.get("content")
            if not isinstance(blocks, list):
                continue
            for block in reversed(blocks):
                if isinstance(block, dict) and block.get("type") == "tool_result":
                    try:
                        payload = json.loads(block.get("content") or "{}")
                    except ValueError:
                        continue
                    result = payload.get("result")
                    if isinstance(result, dict) and result.get("request_id"):
                        ids.append(result["request_id"])
            if len(ids) >= 2:
                break
        mint = _demo_scan(messages, "event_id")
        cited = ids[:2] + ([mint] if mint else [])
        return {"tool_calls": [_t("e14", "record_finding",
            title="JWT weak secret: forged admin token accepted",
            severity="critical", category="jwt", url=base + "/api/me",
            evidence_ids=cited, evidence_excerpt='"role": "admin"',
            description="The secret 'secret123' is dictionary-weak: a forged "
                        "admin token is accepted, while the same request with "
                        "a broken signature is refused 401.",
            remediation="Rotate to a high-entropy secret; prefer asymmetric "
                        "signing.",
            cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H")]}

    scripts = {
        "lead": [
            {"text": "Seeding the pipeline with the most promising "
                     "surfaces.",
             "tool_calls": [
                 _t("l1", "emit_lead", kind="param", url=base + "/item?id=1",
                    params=["id"], note="sql-error surface on id"),
                 _t("l2", "emit_lead", kind="param", url=base + "/search?q=x",
                    params=["q"], note="reflected parameter"),
                 _t("l3", "emit_lead", kind="endpoint",
                    url=base + "/api/user/2", note="enumerable object ids"),
                 _t("l4", "emit_lead", kind="endpoint", url=base,
                    note="web root may serve sensitive artifacts"),
                 _t("l5", "emit_lead", kind="endpoint",
                    url=base + "/api/me",
                    note="bearer-token api - check signing strength")]},
            {"text": "Leads queued; workers drain while I close out.",
             "tool_calls": [_t("l6", "finish_engagement",
                              summary="Team demo: recon mapped the surface, "
                                      "exploit verified SQLi, XSS, IDOR and "
                                      "info disclosure with verbatim "
                                      "evidence.")]},
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
            {"text": "Confirming the injectable id parameter, and reading "
                     "rows: the class needs the engine named plus data.",
             "tool_calls": [_t("e2", "probe_sqli", url=base + "/item?id=1",
                              param="id", union_cols=6,
                              extract_table="users",
                              extract_columns="username,password")]},
            _team_sqli_finding,
            {"text": "A diagnostic endpoint takes a host - probe for output.",
             "tool_calls": [_t("e3b", "probe_cmdi",
                              url=base + "/ping?host=127.0.0.1",
                              param="host")]},
            _team_rce_finding,
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
                                          "add CSP.",
                              cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N")]},
            {"tool_calls": [_t("e6", "probe_idor",
                              url=base + "/api/user/2")]},
            _team_idor_finding,
            {"tool_calls": [_t("e8", "probe_disclosure", url=base)]},
            {"tool_calls": [_t("e9", "record_finding",
                              title="Exposed /.env and /.git/HEAD at web "
                                    "root",
                              severity="medium", category="info-disclosure",
                              url=base + "/.env",
                              evidence_excerpt="SECRET_KEY=lab-secret-0123",
                              description="Sensitive paths served publicly - "
                                          "credentials and VCS metadata "
                                          "leak.",
                              remediation="Deny dotfile/VCS paths; rotate "
                                          "exposed secrets.",
                              cvss="CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N")]},
            {"text": "JWT endpoint last: decode, crack, forge, prove.",
             "tool_calls": [
                 _t("e10", "http_request", method="GET",
                    url=base + "/token?user=alice"),
                 _t("e11", "jwt_decode", token=tok)]},
            {"tool_calls": [
                _t("e12", "jwt_forge", token=tok,
                   claims='{"user":"admin","role":"admin"}',
                   secret="secret123"),
                _t("e13", "http_request", method="GET",
                   url=base + "/api/me",
                   headers={"Authorization": f"Bearer {forged}"})]},
            {"text": "The control: same request, signature broken.",
             "tool_calls": [_t("e13b", "http_request", method="GET",
                              url=base + "/api/me",
                              headers={"Authorization":
                                       f"Bearer {forged[:-4]}AAAA"})]},
            _team_jwt_finding,
            {"tool_calls": [_t("e15", "finish",
                              summary="5/5 leads verified with verbatim "
                                      "evidence.")]},
        ],
    }

    def _factory(role: str, _name: str):
        return ScriptedClient(scripts.get(role, []))

    cfg.max_turns = 15
    return TeamRun(cfg, llm_factory=_factory, quiet=args.quiet,
                   n_recon=1, n_exploit=1, n_report=0).run()


_ARM_METRICS = (
    # (key, label, higher_is_better) - `proven` first because EXPERIMENTS
    # makes it the primary measure: a configuration that records more
    # findings at a lower proven rate is not better, and a total cannot
    # show that.
    ("proven", "proven findings", True),
    ("candidate", "candidates", None),
    ("unproven", "unproven", None),
    ("findings", "findings (total)", None),
    ("requests", "wire requests", False),
    ("ttf", "time to first finding (s)", False),
    ("duration_s", "duration (s)", False),
    ("coverage", "endpoints touched", True),
    ("llm_calls", "llm calls", False),
    ("tokens_in", "tokens in", False),
    ("tokens_out", "tokens out", False),
    ("cache_read", "cache read tokens", False),
    ("cache_write", "cache write tokens", False),
    ("usd", "cost (usd)", False),
)

# A median over the priced subset of an arm would read as the arm's cost
# while describing only part of it, so these report `-` unless every trial
# in the arm carries the figure. `usd` is None whenever the model is absent
# from models.json, which is every scripted demo.
_ARM_METRICS_ALL_OR_NOTHING = ("usd",)


def _arm_of(path) -> str:
    """The configuration a trial belongs to.

    `docs/EXPERIMENTS.md` lays the trials out as `exp/single-1/<session>` and
    `exp/team-3/<session>`, so the arm is the parent directory with a
    trailing `-<trial>` stripped. A session dir given on its own falls back to
    its own name, which makes every such dir its own arm - correct, and
    visible in the N column rather than silently merged.
    """
    import re as _re
    parent = Path(path).resolve().parent.name
    if not parent:
        return Path(path).name
    return _re.sub(r"[-_]\d+$", "", parent) or parent


def _compare_by_arm(dirs, summarise, host_of, csv: bool = False) -> int:
    """Median of each metric per configuration, with N and the spread.

    `EXPERIMENTS.md` asks for medians twice and nothing computed one, so every
    evaluation did it by hand in a spreadsheet - which is exactly where a
    number gets mistyped and no reader can check it.

    The median is `median_low`, not the mean of the middle two: on an even N
    that would report a value no trial produced, and this system's whole claim
    is that it does not invent numbers. The spread is printed beside it
    because a median alone hides a bimodal arm.
    """
    import statistics

    def _flatten(row: dict) -> dict:
        """Lift the nested token and cost figures to scalars.

        `_summ` reports `tokens` as a dict and the cost under `llm_cost`, and
        a median needs a number. `usd` stays `None` when the run's model is
        not in `models.json` - there is no price to apply, and reporting 0
        would claim the run was free.
        """
        out = dict(row)
        tokens = row.get("tokens")
        if isinstance(tokens, dict):
            out["tokens_in"] = tokens.get("in")
            out["tokens_out"] = tokens.get("out")
            out["cache_read"] = tokens.get("cache_read")
            out["cache_write"] = tokens.get("cache_write")
        cost = row.get("cost")
        if isinstance(cost, dict):
            out["usd"] = cost.get("usd")
        return out

    arms: dict[str, list[dict]] = {}
    for d in dirs:
        arms.setdefault(_arm_of(d), []).append(_flatten(summarise(d)))
    if not arms:
        print("compare --by-arm needs at least one session dir")
        return 2

    hosts = {host_of(d) for d in dirs} - {""}
    if len(hosts) > 1:
        print(f"warning: targets differ ({', '.join(sorted(hosts))}) - "
              "metrics only compare like-for-like on the same target",
              file=sys.stderr)
    versions = {s["version"] for s in
                (x for rows in arms.values() for x in rows)
                if isinstance(s.get("version"), str)} - {""}
    if len(versions) > 1:
        print(f"warning: argus versions differ "
              f"({', '.join(sorted(versions))}) - probe counts and detection "
              "logic change between builds", file=sys.stderr)

    def _values(rows, key):
        out = []
        for row in rows:
            value = row.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                continue
            out.append(value)
        if key in _ARM_METRICS_ALL_OR_NOTHING and len(out) != len(rows):
            return []
        return out

    empty = {arm: sum(1 for r in arms[arm] if "findings" not in r)
             for arm in arms}
    if any(empty.values()):
        where = ", ".join(f"{a} ({n})" for a, n in sorted(empty.items()) if n)
        print(f"warning: {where} - session dir(s) with no summary.json. "
              "They count toward N but contribute no metric, which skews "
              "every median in that arm", file=sys.stderr)

    names = sorted(arms)
    if csv:
        print("arm,n,metric,median,min,max")
        for arm in names:
            for key, label, _ in _ARM_METRICS:
                vals = _values(arms[arm], key)
                if not vals:
                    continue
                print(f"{arm},{len(arms[arm])},{key},"
                      f"{statistics.median_low(vals)},{min(vals)},{max(vals)}")
        return 0

    width = max(26, max(len(a) for a in names) + 12)
    print(f"{'metric':<26}" + "".join(
        f"{a + ' (n=' + str(len(arms[a])) + ')':<{width}}" for a in names))
    print("-" * (26 + width * len(names)))
    for key, label, higher in _ARM_METRICS:
        cells = []
        for arm in names:
            vals = _values(arms[arm], key)
            if not vals:
                cells.append("-")
                continue
            med = statistics.median_low(vals)
            lo, hi = min(vals), max(vals)
            spread = "" if lo == hi else f"  [{lo}-{hi}]"
            cells.append(f"{med}{spread}")
        print(f"{label:<26}" + "".join(f"{c:<{width}}" for c in cells))
    print()
    print("median is median_low: on an even N the mean of the middle two "
          "would be a number no trial produced.")
    print("proven is the primary measure - a configuration that records more "
          "findings at a lower proven")
    print("rate is not better, and the total cannot show that.")
    singles = [a for a in names if len(arms[a]) == 1]
    if singles:
        print(f"\nn=1 for {', '.join(singles)}: a single trial has no median. "
              f"EXPERIMENTS suggests 5.")
    return 0


def _cmd_judge(args) -> int:
    """Cross-family verification over a recorded session.

    Deliberately a separate command rather than a step in the run: it costs
    one call per finding on a second provider, and it reads a session that is
    already sealed. Re-sealing afterwards is the same trade `argus report`
    makes - the chain still covers the new state, and `argus verify` says so.
    """
    from . import judge as judge_mod
    from . import models as models_mod
    from .config import _seal_key, resolve_auth, API_URL, DEFAULT_MODEL
    from .session import _atomic_write, findings_bad, verify_transcript

    sdir = Path(args.session_dir)
    if not (sdir / "transcript.jsonl").exists():
        print(f"no transcript.jsonl in {sdir} - not a session dir")
        return 1
    seal = _seal_key(args)
    session = _reopen(sdir, seal)
    if not session._transcript:
        print(f"{sdir} has an empty transcript - nothing to judge")
        return 1

    author = ""
    try:
        author = str(json.loads((sdir / "meta.json").read_text(
            encoding="utf-8")).get("model") or "")
    except Exception:
        pass

    # The chain check must use the SAME key the session was sealed with, or
    # every keyed session is accused of having been edited. `_seal_key(args)`
    # is already resolved above for `_reopen`; pass it on.
    v = verify_transcript(sdir, seal_key=seal)
    if not v.get("chained") or v.get("tail_truncated") or v.get("bad_lines"):
        print("warning: transcript chain check failed - judging an edited "
              "transcript (run 'argus verify')"
              + ("" if seal else "; if this session was sealed with a key, "
                 "pass --seal-key"), file=sys.stderr)
    bad = findings_bad(session._transcript, session.findings)

    wanted = {x.strip() for x in str(args.only or "").split(",") if x.strip()}
    rows = [f for f in session.findings if isinstance(f, dict)
            and (not wanted or f.get("id") in wanted)
            and f.get("id") not in bad]
    if wanted:
        known_ids = {str(f.get("id")) for f in session.findings
                     if isinstance(f, dict)}
        unknown = sorted(wanted - known_ids)
        if unknown:
            print(f"--only names {unknown}, which this session has no "
                  f"finding for. It has: {sorted(known_ids) or 'none'}")
            return 2
    if not rows:
        print("no findings to judge"
              + (f" (excluded by evidence re-validation: {sorted(bad)})"
                 if bad else ""))
        return 0

    def cited(finding):
        return [session._transcript[i] for i in (finding.get("evidence_ids")
                                                 or [])
                if i in session._transcript]

    if args.dry_run:
        for finding in rows:
            print(f"===== case file for {finding.get('id')} =====")
            print(judge_mod.render_case(finding, cited(finding)))
        return 0

    if args.judge_model:
        spec = models_mod.get(args.judge_model)
        if spec is None:
            print(f"{args.judge_model} is not in models.json; "
                  f"`argus models` lists what is")
            return 2
        if author and models_mod.family(args.judge_model) == \
                models_mod.family(author):
            print(f"{args.judge_model} is the same family as {author}, which "
                  "the run already used - two models that agree because they "
                  "share a prior are not a check. Name another, or let the "
                  "table pick.")
            return 2
        # The role gate applies to a named model too. Without this, --judge-model
        # accepted anything in the table - including a model the table lists
        # only for `breadth` or `writer`, which is not an opinion worth having
        # about a proof.
        if "judge" not in spec.roles:
            print(f"{args.judge_model} is not listed for the judge role "
                  f"(it serves: {', '.join(spec.roles) or 'nothing'}). "
                  f"`argus models` shows which models are. Reviewing a proof "
                  f"is not a job every model is listed for.")
            return 2
        pick = spec
    else:
        pick = judge_mod.pick_judge(author or DEFAULT_MODEL, args.policy)
    if pick is None:
        print(f"no judge available: every model listed for the judge role "
              f"outside {models_mod.family(author or DEFAULT_MODEL)!r} needs "
              f"a credential that is not set. `argus models` shows which. "
              f"Running the author's own family as its own reviewer would "
              f"not be cross-verification.")
        return 2

    key, tok = resolve_auth(args)
    cfg = Config(target="http://x", model=pick.key, api_key=key or "",
                 auth_token=tok or "", api_base=API_URL)
    if pick.provider == "anthropic" and not (key or tok):
        print("no Anthropic credential found for the judge - set "
              "ANTHROPIC_API_KEY or sign in to Claude Code")
        return 1
    from .llm import make_client
    llm = make_client(cfg)
    print(f"judge: {pick.key} ({pick.provider}); author: {author or '?'}; "
          f"{len(rows)} finding(s)", file=sys.stderr)

    verdicts, updated = [], []
    for finding in session.findings:
        if not isinstance(finding, dict) or finding not in rows:
            updated.append(finding)
            continue
        verdict = judge_mod.judge_finding(llm, finding, cited(finding),
                                          pick.key)
        verdicts.append(verdict)
        updated.append(judge_mod.apply_verdict(finding, verdict))
    session.findings = updated

    session.record_event("cross_verification", {
        "judge_model": pick.key, "author_model": author,
        "verdicts": [x.to_dict() for x in verdicts]})
    _atomic_write(session.findings_path,
                  json.dumps(session.findings, indent=2, ensure_ascii=False))

    # Re-render before sealing. Writing the verdict into findings.json and
    # then sealing left report.md, report.html, report.sarif and summary.json
    # describing findings that no longer matched - a reader opening the report
    # saw a `proven` finding with no sign a judge had disputed it, under a
    # seal that covered both. The report is the deliverable; it has to say
    # what the record says.
    try:
        from .report.markdown import render_report
        prior = {}
        spath = session.dir / "summary.json"
        if spath.exists():
            try:
                loaded = json.loads(spath.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    prior = loaded
            except (ValueError, OSError):
                prior = {}
        render_report(session, cfg, str(prior.get("agent_summary") or ""),
                      extra={"cross_verified_by": pick.key,
                             "cross_verified_at": int(time.time())})
    except Exception as exc:
        # a render failure must not lose the verdicts already written
        print(f"warning: report re-render failed after judging: {exc}; "
              f"findings.json carries the verdicts and the report does not",
              file=sys.stderr)

    if args.json:
        print(json.dumps([x.to_dict() for x in verdicts], indent=2,
                         ensure_ascii=False))
    else:
        for x in verdicts:
            mark = "AGREES " if x.agrees else "DISPUTES"
            print(f"{mark} {x.finding_id}: {x.reason or x.error}")
            if x.missing:
                print(f"         would settle it: {'; '.join(x.missing)}")
    try:
        session.seal_artifacts()
    except OSError as exc:
        print(f"warning: re-seal failed: {exc}", file=sys.stderr)
    disputed = sum(1 for x in verdicts if not x.agrees)
    print(f"\n{len(verdicts) - disputed} agreed, {disputed} disputed. "
          f"Grades are unchanged: a judge cannot promote a finding.",
          file=sys.stderr)
    return 0


def _reopen(sdir: Path, seal_key: str = "") -> Session:
    """Rebuild a Session view over an existing session directory.

    `seal_key` matters here: `argus report` re-seals, and chaining the seal
    entry unkeyed over a keyed transcript would break the chain this command
    exists to preserve.
    """
    import threading
    sess = Session.__new__(Session)
    sess.dir = sdir
    sess.id = sdir.name
    sess.started = 0.0
    sess._seq = 0
    sess._transcript = {}
    sess._lock = threading.Lock()
    sess._last_chain = ""
    sess.resumed = False
    sess.require_proof = False
    sess.seal_key = str(seal_key or "")
    # __init__ is bypassed, so keep the attribute surface COMPLETE: a reopened
    # session used to AttributeError on `secret_values` (note()/record_*/_log
    # all read it), and `record_event` redacts against it - so any command
    # recording into an existing session died instead of writing its entry.
    # There are no live credentials to redact on a reopen: the run that held
    # them is over, and anything they touched was redacted on the way in.
    sess.secret_values = set()
    mpath = sdir / "meta.json"
    if mpath.is_file():
        try:
            meta = json.loads(mpath.read_text(encoding="utf-8"))
            if isinstance(meta, dict):
                sess.started = float(meta.get("started") or 0.0)
        except (ValueError, OSError):
            pass
    tpath = sdir / "transcript.jsonl"
    if tpath.is_file():
        # forensic reader: skip malformed lines - `argus verify` reports
        # them; crashing here would hide the rest of a damaged transcript
        try:
            lines = tpath.read_text(encoding="utf-8").splitlines()
        except OSError:
            lines = []
        for line in lines:
            if not line.strip():
                continue
            try:
                entry = json.loads(line)
            except ValueError:
                continue
            if not isinstance(entry, dict) or not isinstance(
                    entry.get("id"), str):
                continue
            sess._transcript[entry["id"]] = entry
            if entry.get("chain"):
                sess._last_chain = entry["chain"]
            sess._seq = max(sess._seq, int(entry["id"][1:]) if entry["id"][1:].isdigit() else 0)
    fpath = sdir / "findings.json"
    try:
        rows = json.loads(fpath.read_text(encoding="utf-8")) \
            if fpath.is_file() else []
    except (ValueError, OSError):
        rows = []
    sess.findings = rows if isinstance(rows, list) else []
    return sess


if __name__ == "__main__":
    sys.exit(main())
