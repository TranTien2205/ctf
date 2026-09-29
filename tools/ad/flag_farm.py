#!/usr/bin/env python3
"""Run one exploit against every team, every tick, and submit what comes back.

The unit of work in attack-defense is not "a flag" but "a flag per team per
tick", so the jeopardy control loop in this tree does not fit: tools/hooks.py
gates ONE verified flag, and decide.py budgets probes against ONE target. This
tool is the sibling loop for the other mode, and it deliberately does not touch
challenges/<name>/state.json.

    flag_farm.py config.json              # loop until stopped
    flag_farm.py config.json --once       # one tick, for testing the exploit
    flag_farm.py config.json --dry-run    # run exploits, submit nothing

Config, written by the operator, e.g.

    {
      "authorized_event": "Security Bootcamp Arena 2026",
      "service": "notes",
      "teams": [
        {"id": 1, "host": "10.60.1.1"},
        {"id": 2, "host": "10.60.2.1"}
      ],
      "exploit": ["python3", "sploits/notes.py", "{host}"],
      "flag_regex": "[A-Z0-9]{31}=",
      "submit": {"url": "http://10.10.10.10/flags", "header": "X-Team-Token",
                 "token": "...."},
      "tick_seconds": 60,
      "exploit_timeout": 25,
      "skip_self": 3
    }

Two guards, on purpose:

  * it refuses to start unless `authorized_event` is set and `teams` is an
    explicit list. There is no CIDR expansion and no discovery, so it can only
    ever hit hosts the operator typed. This is a contest tool, not a scanner.
  * it never submits the same flag twice, because most scoreboards penalise
    duplicate submissions and the same flag will be re-stolen every tick until
    the target rotates it.

The most valuable output is not the flag count. It is `immune`: a team that
stops yielding flags while the others still do has patched, and their patch is
the fastest description of the bug you are exploiting. Go and read it.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor


def load_config(path):
    with open(path, encoding="utf-8") as fh:
        cfg = json.load(fh)
    problems = []
    if not cfg.get("authorized_event"):
        problems.append("authorized_event is missing: name the contest this is for")
    teams = cfg.get("teams")
    if not isinstance(teams, list) or not teams:
        problems.append("teams must be an explicit non-empty list of {id, host}")
    else:
        for t in teams:
            if not isinstance(t, dict) or "host" not in t:
                problems.append("every team needs a host: %r" % (t,))
                break
            if "/" in str(t.get("host", "")):
                problems.append("a host looks like a CIDR range (%r); list hosts "
                                "individually" % t["host"])
                break
    if not cfg.get("exploit"):
        problems.append("exploit must be an argv list, with {host} where the target goes")
    if not cfg.get("flag_regex"):
        problems.append("flag_regex is required; get the exact format from the rules")
    if problems:
        raise SystemExit(json.dumps({"error": "config rejected", "problems": problems},
                                    indent=1))
    return cfg


def run_exploit(cfg, team):
    """Run the exploit for one team. Returns a result dict; never raises."""
    argv = [a.replace("{host}", str(team["host"])).replace("{id}", str(team.get("id", "")))
            for a in cfg["exploit"]]
    timeout = float(cfg.get("exploit_timeout", 25))
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, capture_output=True, timeout=timeout,
                              env={**os.environ, "TARGET_HOST": str(team["host"])})
        # Scan stderr too: plenty of quick exploits print the flag with a bare
        # print() to one stream and diagnostics to the other, and losing a flag
        # because it came out of the wrong pipe is a silly way to lose points.
        out = (proc.stdout.decode("utf-8", "replace")
               + "\n" + proc.stderr.decode("utf-8", "replace"))
        err = proc.stderr.decode("utf-8", "replace")[:300]
        code = proc.returncode
    except subprocess.TimeoutExpired:
        return {"team": team.get("id"), "host": team["host"], "flags": [],
                "status": "timeout", "seconds": round(time.monotonic() - started, 2)}
    except Exception as exc:
        return {"team": team.get("id"), "host": team["host"], "flags": [],
                "status": "error: %s" % exc, "seconds": 0}

    flags = sorted(set(re.findall(cfg["flag_regex"], out)))
    return {
        "team": team.get("id"),
        "host": team["host"],
        "flags": flags,
        # A non-zero exit with flags on stdout is still a win; report the code
        # rather than discarding the flags, because a sloppy exploit often exits
        # non-zero after it has already printed.
        "status": "ok" if flags else ("exit %d" % code),
        "stderr": err if not flags else "",
        "seconds": round(time.monotonic() - started, 2),
    }


def submit(cfg, flags, dry_run=False):
    """Send flags to the scoreboard. Returns (accepted_text, error)."""
    sub = cfg.get("submit") or {}
    if dry_run or not sub.get("url"):
        return ("dry-run: %d flag(s) not submitted" % len(flags), None)
    payload = json.dumps(list(flags)).encode()
    headers = {"Content-Type": "application/json"}
    if sub.get("header") and sub.get("token"):
        headers[sub["header"]] = sub["token"]
    req = urllib.request.Request(sub["url"], data=payload, headers=headers, method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=float(sub.get("timeout", 10))) as r:
            return (r.read(4000).decode("utf-8", "replace"), None)
    except urllib.error.HTTPError as exc:
        return (exc.read(2000).decode("utf-8", "replace"), "HTTP %s" % exc.code)
    except Exception as exc:
        return ("", "%s: %s" % (type(exc).__name__, exc))


def tick(cfg, seen, dry_run=False):
    # Only skip when skip_self is actually configured; otherwise a team that
    # simply has no id would match None and be silently dropped every tick.
    mine = cfg.get("skip_self")
    teams = ([t for t in cfg["teams"] if t.get("id") != mine]
             if mine is not None else list(cfg["teams"]))
    workers = min(len(teams), int(cfg.get("workers", 16))) or 1
    with ThreadPoolExecutor(max_workers=workers) as ex:
        results = list(ex.map(lambda t: run_exploit(cfg, t), teams))

    fresh = []
    for r in results:
        for f in r["flags"]:
            if f not in seen:
                seen.add(f)
                fresh.append(f)

    accepted, err = submit(cfg, fresh, dry_run) if fresh else ("no new flags", None)

    yielding = [r["team"] for r in results if r["flags"]]
    immune = [r["team"] for r in results if not r["flags"]]
    return {
        "service": cfg.get("service"),
        "teams_tried": len(results),
        "teams_yielding": yielding,
        # The line worth reading every tick.
        "immune": immune,
        "immune_note": ("these teams gave nothing while others did: they have "
                        "patched, and their patch is the shortest description of "
                        "the bug -- go read it" if immune and yielding else ""),
        "new_flags": len(fresh),
        "total_unique": len(seen),
        "submit": accepted[:300],
        "submit_error": err,
        "per_team": results,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--once", action="store_true", help="one tick and exit")
    ap.add_argument("--dry-run", action="store_true", help="run exploits, submit nothing")
    ap.add_argument("--state", default=None,
                    help="file of already-submitted flags, so a restart does not resubmit")
    args = ap.parse_args()

    cfg = load_config(args.config)
    state_path = args.state or (os.path.splitext(args.config)[0] + ".seen")
    seen = set()
    if os.path.exists(state_path):
        with open(state_path, encoding="utf-8") as fh:
            seen = {line.strip() for line in fh if line.strip()}

    period = float(cfg.get("tick_seconds", 60))
    while True:
        start = time.monotonic()
        out = tick(cfg, seen, args.dry_run)
        out["event"] = cfg["authorized_event"]
        print(json.dumps(out, ensure_ascii=False), flush=True)

        with open(state_path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(sorted(seen)))

        if args.once:
            return 0
        slept = period - (time.monotonic() - start)
        if slept > 0:
            time.sleep(slept)


if __name__ == "__main__":
    sys.exit(main())
