#!/usr/bin/env python3
"""Recon intake for a bare live target, as one command.

Runs the bounded trio -- tools/web_probe.py, tools/web_enum.py and
tools/web/bundle_miner.py -- on the supplied URL, host:port or domain, and
emits the observation list tools/classify.py consumes, plus the classify
command with the text already composed. It replaces the hand-assembly step
that used to sit between recon and classification.

It never claims a vulnerability: every entry in `observations` is verbatim
from one of the three tool outputs. Scope is the supplied target only; the
trio is the same three commands the Loop's minimal-recon rule allows, and
schemeless input is tried on http first and https second -- never both at
once, never any other host or port.
"""
import argparse
import json
import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from ctf import bare_live_target  # noqa: E402

PROBE = os.path.join(ROOT, "tools", "web_probe.py")
ENUM = os.path.join(ROOT, "tools", "web_enum.py")
MINER = os.path.join(ROOT, "tools", "web", "bundle_miner.py")


def run_tool(cmd, timeout):
    """One bounded subprocess; returns (parsed_json_or_None, record)."""
    started = time.monotonic()
    record = {"cmd": " ".join(os.path.basename(c) if c.endswith(".py") else c
                              for c in cmd)}
    try:
        out = subprocess.run([sys.executable] + cmd, capture_output=True,
                             text=True, timeout=timeout)
        record["elapsed"] = round(time.monotonic() - started, 3)
        record["exit"] = out.returncode
        if out.returncode != 0 and not out.stdout.strip():
            record["error"] = (out.stderr or "no output").strip()[:200]
            return None, record
        try:
            return json.loads(out.stdout), record
        except json.JSONDecodeError:
            record["error"] = "stdout was not JSON: " + out.stdout[:160]
            return None, record
    except subprocess.TimeoutExpired:
        record["error"] = "timed out after %ds" % timeout
        return None, record
    except OSError as exc:
        record["error"] = str(exc)
        return None, record


def base_candidates(target):
    """The supplied target as URL(s). Schemeless input tries http then https;
    anything else stays out of scope."""
    if "://" in target:
        return [target]
    return ["http://" + target, "https://" + target]


def reachable(probe_json):
    if not probe_json:
        return False
    p = probe_json.get("probe") or {}
    return p.get("result") == "response" and p.get("status") is not None


def observations(probe, enum, miner):
    """Verbatim facts only, phrased the way classify.py's signal scan reads
    them: stack words, endpoint paths, parameter names, artifact kinds."""
    obs = []
    if probe:
        p = probe.get("probe") or {}
        parts = ["%s returns %s %s" % (probe.get("url"), p.get("status"),
                                       p.get("content_type"))]
        headers = p.get("headers") or {}
        for name in ("Server", "X-Powered-By", "Set-Cookie", "Via",
                     "CF-RAY", "X-AspNet-Version"):
            if headers.get(name):
                parts.append("%s: %s" % (name, headers[name]))
        if p.get("final_url") and p["final_url"] != probe.get("url"):
            parts.append("redirects to %s" % p["final_url"])
        obs.append("; ".join(parts))
        for ep in (p.get("endpoints") or [])[:20]:
            obs.append("page references endpoint %s" % ep)
        for form in (p.get("forms") or [])[:10]:
            if isinstance(form, dict):
                obs.append("form %s %s params %s"
                           % (form.get("method", "GET"), form.get("action"),
                              ",".join(form.get("params", []) or [])))
            else:
                obs.append("form %s" % form)
        for param in (p.get("parameters") or [])[:20]:
            obs.append("parameter %s" % param)
        if p.get("artifact"):
            obs.append("response artifact kind: %s" % p["artifact"])
    if enum:
        for item in (enum.get("paths") or [])[:30]:
            obs.append("path %s -> %s" % (item.get("path"), item.get("status")))
        for prefix in (enum.get("static_prefixes") or [])[:10]:
            obs.append("static prefix %s" % prefix)
        for ep in (enum.get("js_endpoints") or [])[:30]:
            obs.append("front-end calls %s" % ep)
        for row in (enum.get("method_matrix") or [])[:20]:
            verbs = ", ".join("%s=%s" % (k, v) for k, v in row.items()
                              if k != "path")
            obs.append("method matrix %s: %s" % (row.get("path"), verbs))
    if miner:
        for ep in (miner.get("endpoints") or [])[:40]:
            methods = ",".join(ep.get("methods") or [])
            obs.append("bundle endpoint %s (%s)" % (ep.get("path"),
                                                    methods or "methods?"))
        for route in (miner.get("routes") or [])[:30]:
            if isinstance(route, dict):
                obs.append("front-end route %s" % route.get("path", route))
            else:
                obs.append("front-end route %s" % route)
        if miner.get("env_refs"):
            obs.append("%d front-end env var refs" % len(miner["env_refs"]))
        if miner.get("secret_candidates"):
            obs.append("%d secret CANDIDATES in bundle (shape/entropy only, "
                       "never validated)" % len(miner["secret_candidates"]))
        if miner.get("verdict_line"):
            obs.append("bundle verdict: %s" % miner["verdict_line"])
    return obs


def intake(target, timeout):
    """The bounded trio on one target; a dict the caller can print."""
    if not bare_live_target(target):
        return {"mode": "recon-intake", "error": "input is not a bare live "
                "target (URL, host:port or domain only); if it carries an "
                "observation, feed it to tools/classify.py directly",
                "input": target}
    records, probe, enum, miner = [], None, None, None
    base = None
    for candidate in base_candidates(target):
        probe, rec = run_tool([PROBE, candidate], timeout)
        records.append(rec)
        if reachable(probe):
            base = candidate
            break
        probe = None
    if base is None:
        return {"mode": "recon-intake", "input": target, "commands_run": records,
                "observations": ["target did not answer an HTTP request on "
                                 "the supplied port"],
                "next_action": ("the target is not HTTP: banner-grab the port "
                                "per skills/target-recon/references/ type-* "
                                "modules, then classify.py on what answers")}
    enum, rec = run_tool([ENUM, base], timeout * 4)
    records.append(rec)
    miner, rec = run_tool([MINER, "--url", base], timeout * 4)
    records.append(rec)
    obs = observations(probe, enum, miner)
    text = "observation: " + "; ".join(obs)
    return {"mode": "recon-intake", "input": target, "base": base,
            "commands_run": records, "observations": obs,
            "observation_text": text,
            "next_action": 'python3 tools/classify.py "%s"' % text}


def selftest():
    """Offline: serve a one-page fixture on 127.0.0.1 and run the real trio."""
    import http.server
    import tempfile
    import threading

    page = ('<html><title>recon-fixture</title>'
            '<script src="/static/app.js"></script></html>')
    bundle = 'fetch("/api/flag?token="); fetch("/api/items/"+id);'
    with tempfile.TemporaryDirectory() as tmp:
        os.makedirs(os.path.join(tmp, "static"))
        with open(os.path.join(tmp, "index.html"), "w") as fh:
            fh.write(page)
        with open(os.path.join(tmp, "static", "app.js"), "w") as fh:
            fh.write(bundle)
        class Quiet(http.server.SimpleHTTPRequestHandler):
            def log_message(self, *args):
                pass  # request logs on stderr would pollute the JSON output
        import functools
        server = http.server.HTTPServer(
            ("127.0.0.1", 0), functools.partial(Quiet, directory=tmp))
        port = server.server_address[1]
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            result = intake("127.0.0.1:%d" % port, timeout=10)
        finally:
            server.shutdown()
    checks = {
        "base_answered": result.get("base", "").startswith("http://127.0.0.1"),
        "status_observed": any("returns 200" in o
                               for o in result.get("observations", [])),
        "js_endpoints_seen": any("/api/flag" in o
                                 for o in result.get("observations", [])),
        "classify_command_emitted": "tools/classify.py" in
        result.get("next_action", ""),
        "three_commands_bound": len(result.get("commands_run", [])) == 3,
    }
    ok = all(checks.values())
    return {"mode": "recon-intake-selftest", "checks": checks, "ok": ok,
            "commands_run": result.get("commands_run")}


def main():
    parser = argparse.ArgumentParser(
        description="Bounded recon intake for a bare live target")
    parser.add_argument("target", nargs="?",
                        help="URL, host:port or domain (nothing else)")
    parser.add_argument("--timeout", type=int, default=15,
                        help="per-command bound in seconds (default 15)")
    parser.add_argument("--selftest", action="store_true",
                        help="offline check against a local fixture server")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        result = selftest()
    else:
        if not args.target:
            parser.error("provide a target or --selftest")
        result = intake(args.target, args.timeout)
    print(json.dumps(result, ensure_ascii=False) if args.json
          else json.dumps(result, ensure_ascii=False, indent=2))
    if args.selftest:
        return 0 if result["ok"] else 1
    return 2 if result.get("error") else 0


if __name__ == "__main__":
    sys.exit(main())
