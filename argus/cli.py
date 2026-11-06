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
    p.add_argument("--session-dir", default="sessions")
    p.add_argument("--allow-private", action="store_true",
                   help="Permit private/loopback targets (auto-allowed if target is private)")
    p.add_argument("--tls-verify", action="store_true",
                   help="Verify TLS certificates (default off for labs/self-signed)")
    p.add_argument("--no-external", action="store_true",
                   help="Disable sqlmap/nuclei/nmap/ffuf/curl wrapper")
    p.add_argument("--llm-max-tokens", type=int, default=4096)
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

    return 2


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
