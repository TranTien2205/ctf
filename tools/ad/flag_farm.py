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
                 "token": "....", "method": "PUT", "format": "json-array"},
      "tick_seconds": 60,
      "exploit_timeout": 25,
      "skip_self": 3
    }

Guards, on purpose:

  * it refuses to start unless `authorized_event` is set and `teams` is an
    explicit list, and every host must be ONE address or ONE hostname. A range,
    a wildcard, a comma list or a shell metacharacter is refused by name -- see
    `check_host()`, which is the function that makes "it can only reach hosts the
    operator typed" true rather than merely claimed. This is a contest tool, not
    a scanner.
  * it never submits the same flag twice, because most scoreboards penalise
    duplicate submissions and the same flag will be re-stolen every tick until
    the target rotates it.
  * `flag_regex` is compiled at load time and refused if it carries a capturing
    group, because `re.findall` would then return the group instead of the flag.
  * an unknown `submit.format` is refused at load time by name. A typo found at
    minute zero costs nothing; the same typo found at minute sixty has cost you
    every flag in between.

The submission dialect is configuration, not code. `submit.method` (default
`PUT`), `submit.format` (default `json-array`; also `newline` and `form`) and
`submit.field` (the field name used by `form`) are read by `build_submission()`,
which is pure -- so the dialect can be proved by the offline selftest instead of
by the first real submission of the contest. The defaults are byte-for-byte what
this tool sent before those keys existed, so a config written earlier behaves
identically. The `submit.field` default is `"flag"`, which is a guess and not a
standard: take the real field name from the rules. Discovering at minute three
that the scoreboard wants POST and a form body, with no way to change it but
editing Python, is how an entire attack score is lost.

A flag is HELD, not lost, when the scoreboard is unreachable. `seen` means
SUBMITTED and `pending` means OBSERVED BUT NOT YET ACCEPTED; a flag moves from
pending to seen only on a submission that really happened and really succeeded.
Both sets are persisted next to the config (`<config>.seen`, `<config>.pending`),
so a restart mid-outage still retries. This matters more than it sounds: at a
60-second tick across eight teams, a 90-second scoreboard outage is about sixteen
flags, and the older behaviour marked them submitted forever.

The most valuable output is not the flag count. It is `immune`: a team that
stops yielding flags while the others still do has patched, and their patch is
the fastest description of the bug you are exploiting. Go and read it.

`immune` is the narrow, honest list and nothing else. A team that returned no
flag did so for one of three different reasons, and only one of them is a patch,
so the non-yielding teams are split by the status that was actually recorded:
`unreachable` (the exploit timed out -- availability evidence about them, worth
one manual curl), `exploit_broken` (the exploit raised before it could finish --
your problem, not theirs) and `immune` (it ran to completion and returned
nothing). In the first hour after an incident, hosts being down is the default
state, so an `immune` list that swallows timeouts is mostly noise exactly when
it is trusted most.
"""
import argparse
import ipaddress
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor


# A single explicit host, and nothing that can expand into more than one. The
# underscore is allowed because contest DNS does hand out such names and it
# carries no range or shell meaning.
HOSTNAME = re.compile(
    r"^[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?"
    r"(\.[a-z0-9_]([a-z0-9_-]{0,61}[a-z0-9_])?)*$", re.I)
BAD_IN_HOST = ("/", "*", ",", " ", "\t", "\n", "\r", "?", "[", "]", ";", "|", "&",
               "$", "`", "(", ")", "\\", "'", '"', "{", "}", "<", ">", "!")


# The three submission dialects this tool can speak. They are listed here rather
# than inline so load_config and build_submission cannot drift apart, and so the
# refusal message can name every valid value.
SUBMIT_FORMATS = ("json-array", "newline", "form")


def check_host(h):
    """Return a problem string, or None when `h` is one explicit target.

    The guard has to refuse a range without refusing a legitimate host: a guard
    that rejects `web1-2.example.com` is a guard the operator switches off at
    hour four, and then nothing is checked at all.
    """
    s = str(h)
    if not s or s != s.strip():
        return ("a host is empty or padded with whitespace (%r): write one "
                "explicit host" % (h,))
    for ch in BAD_IN_HOST:
        if ch in s:
            return ("host %r contains %r: a range, a list or a shell "
                    "metacharacter here turns one exploit into discovery against "
                    "hosts the event did not assign you. Write one explicit host "
                    "per team." % (h, ch))
    try:
        ip = ipaddress.ip_address(s)
    except ValueError:
        pass
    else:
        if ip.is_multicast or ip.is_unspecified or ip.is_reserved:
            return ("host %r is a multicast, unspecified or reserved address, "
                    "not a team" % (h,))
        return None
    if ":" in s:
        return ("host %r carries a port: the port belongs in the exploit argv, "
                "not in the team host" % (h,))
    # Only treat digit-dash-digit as an nmap range when there are no letters at
    # all, or this rejects web1-2.example.com.
    if re.search(r"\d-\d", s) and not any(c.isalpha() for c in s):
        return ("host %r looks like a numeric range: list each host "
                "individually" % (h,))
    if not HOSTNAME.match(s):
        return "host %r is not a single hostname or IP address" % (h,)
    return None


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
        # Report EVERY offending team, not the first. An operator fixing a
        # twelve-host list should not learn about one error per run.
        for t in teams:
            if not isinstance(t, dict) or "host" not in t:
                problems.append("every team needs a host: %r" % (t,))
                continue
            problem = check_host(t.get("host"))
            if problem:
                problems.append(problem)
    if not cfg.get("exploit"):
        problems.append("exploit must be an argv list, with {host} where the target goes")
    rx_src = cfg.get("flag_regex")
    if not rx_src:
        problems.append("flag_regex is required; get the exact format from the rules")
    else:
        try:
            rx = re.compile(rx_src)
        except re.error as exc:
            problems.append("flag_regex does not compile: %s" % exc)
        else:
            if rx.groups:
                problems.append(
                    "flag_regex has %d capturing group(s): a group makes the "
                    "extractor return the GROUP instead of the whole match, so "
                    "every flag would be submitted with its wrapper stripped and "
                    "rejected for the whole contest. Use a non-capturing group "
                    "(?:...) instead of (...)." % rx.groups)
    sub = cfg.get("submit")
    if sub is None:
        sub = {}
    if not isinstance(sub, dict):
        problems.append("submit must be an object, not %s" % type(sub).__name__)
    elif sub.get("format", "json-array") not in SUBMIT_FORMATS:
        problems.append(
            "submit.format %r is not one of %s. This is refused now because the "
            "alternative is discovering it from a scoreboard that rejects every "
            "flag, an hour in." % (sub.get("format"), ", ".join(SUBMIT_FORMATS)))
    if problems:
        raise SystemExit(json.dumps({"error": "config rejected", "problems": problems},
                                    indent=1))
    # Not fatal, but it must be said out loud once: without skip_self your own
    # team is in the attack list and your own flag goes to the scoreboard.
    cfg["_warnings"] = ([] if cfg.get("skip_self") is not None else
                        ["skip_self is not set: your own team is in the attack "
                         "list and your own flag will be submitted. Set skip_self "
                         "to your team id."])
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

    # group(0), not findall: findall with a capturing group returns the group,
    # which would strip the flag's wrapper. load_config refuses such a regex,
    # but the guard is advice and group(0) is arithmetic.
    flags = sorted({m.group(0) for m in re.finditer(cfg["flag_regex"], out)})
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


def build_submission(cfg, flags):
    """Return (method, url, headers, body_bytes) for one submission.

    Pure on purpose: it opens no socket, so the scoreboard dialect is provable by
    the offline selftest rather than by the first real submission. The defaults
    -- PUT, a bare JSON array, `application/json` -- are exactly what this tool
    sent before the keys existed.

    Raises ValueError on an unknown format. load_config already refuses one at
    startup; this is the arithmetic behind that advice, for a config that was
    edited while the loop was running.
    """
    sub = cfg.get("submit") or {}
    fmt = sub.get("format", "json-array")
    items = list(flags)
    if fmt == "json-array":
        body = json.dumps(items).encode()
        ctype = "application/json"
    elif fmt == "newline":
        # Trailing newline included: a line-oriented reader on the other side
        # drops the last line without it, which loses exactly one flag per batch.
        body = ("\n".join(items) + "\n").encode()
        ctype = "text/plain"
    elif fmt == "form":
        # One repeated field, not a joined string: a scoreboard that takes a form
        # almost always reads a repeated key, and urlencode escapes the flag so a
        # wrapper containing & or = survives.
        body = urllib.parse.urlencode(
            [(sub.get("field", "flag"), f) for f in items]).encode()
        ctype = "application/x-www-form-urlencoded"
    else:
        raise ValueError(
            "submit.format %r is not one of %s" % (fmt, ", ".join(SUBMIT_FORMATS)))
    headers = {"Content-Type": ctype}
    # Both keys, or neither. A header name with no token sends an empty
    # credential, which some scoreboards answer 200 to and score nothing.
    if sub.get("header") and sub.get("token"):
        headers[sub["header"]] = sub["token"]
    return (str(sub.get("method", "PUT")).upper(), sub.get("url"), headers, body)


def submit(cfg, flags, dry_run=False):
    """Send flags to the scoreboard.

    Returns (accepted_text, error, submitted_for_real). The third value exists
    because there are TWO branches that submit nothing and report no error -- a
    dry run, and a config whose submit.url is not filled in yet, which is exactly
    the state at minute 20 of the runbook. A caller that drained its pending set
    on `error is None` would discard flags in both.
    """
    sub = cfg.get("submit") or {}
    # This short-circuit stays AHEAD of anything that builds or sends a request.
    # Widening it wrongly is how --dry-run starts submitting.
    if dry_run or not sub.get("url"):
        return ("dry-run: %d flag(s) not submitted" % len(flags), None, False)
    try:
        method, url, headers, payload = build_submission(cfg, flags)
    except ValueError as exc:
        # Nothing left the process, so submitted_for_real is False and the flags
        # stay pending. The error is still reported, so three ticks of this trip
        # the ALERT rather than failing quietly.
        return ("", "config: %s" % exc, False)
    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=float(sub.get("timeout", 10))) as r:
            return (r.read(4000).decode("utf-8", "replace"), None, True)
    except urllib.error.HTTPError as exc:
        return (exc.read(2000).decode("utf-8", "replace"), "HTTP %s" % exc.code, True)
    except Exception as exc:
        return ("", "%s: %s" % (type(exc).__name__, exc), True)


def tick(cfg, seen, pending, dry_run=False):
    """One round against every team.

    `seen` is SUBMITTED, `pending` is OBSERVED BUT NOT YET ACCEPTED. The batch is
    the whole pending set, not just this tick's finds, so a flag from a failed
    tick retries by itself.
    """
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
            if f not in seen and f not in pending:
                pending.add(f)
                fresh.append(f)

    batch = sorted(pending)
    if batch:
        accepted, err, for_real = submit(cfg, batch, dry_run)
    else:
        accepted, err, for_real = ("no new flags", None, False)

    # The only place a flag leaves `pending`: a submission that really happened
    # and really succeeded.
    submitted_ok = bool(for_real and err is None)
    if submitted_ok:
        for f in batch:
            pending.discard(f)
            seen.add(f)

    # Bucket the non-yielding teams by what was actually observed. "returned no
    # flag" is three different facts wearing one name: a team that patched, a
    # team whose host is down, and an exploit that never ran. The operator acts
    # harder on this line than on any other, so conflating them spends the most
    # expensive half hour of the contest hunting a patch on a box that is simply
    # offline. It is the attack-defense form of this tree's rule that a timeout
    # is evidence about availability, not evidence about a bug.
    yielding = [r["team"] for r in results if r["flags"]]
    silent, unreachable, broken = [], [], []
    for r in results:
        if r["flags"]:
            continue
        status = str(r.get("status") or "")
        if status == "timeout":
            unreachable.append(r["team"])
        elif status.startswith("error:"):
            broken.append(r["team"])
        else:
            # "exit <code>" and anything else: the exploit ran to completion and
            # produced nothing. A non-zero exit lands here too, because an
            # exploit that prints the flag and then exits non-zero is common and
            # the exit code alone cannot tell the two apart.
            silent.append(r["team"])
    # `immune` keeps its name and its place; its meaning narrows to the subset
    # the word can honestly describe.
    immune = silent
    out = {
        "service": cfg.get("service"),
        "teams_tried": len(results),
        "teams_yielding": yielding,
        # The line worth reading every tick -- and only the teams it can claim.
        "immune": immune,
        "immune_note": ("these teams ran the exploit to completion and returned "
                        "nothing while others returned flags: they have patched, "
                        "and their patch is the shortest description of the bug "
                        "-- go read it" if immune and yielding else ""),
        "unreachable": unreachable,
        "unreachable_note": ("the exploit timed out against these teams. That is "
                             "availability evidence about THEM, not evidence that "
                             "they patched: worth one manual curl, not a patch "
                             "hunt" if unreachable else ""),
        "exploit_broken": broken,
        "exploit_broken_note": ("the exploit raised before it could finish against "
                                "these teams: fix your own exploit before reading "
                                "anything into this result" if broken else ""),
        "new_flags": len(fresh),
        "pending_flags": len(pending),
        "submitted_ok": submitted_ok,
        "submitted_this_tick": len(batch) if submitted_ok else 0,
        "submitted_total": len(seen),
        # Unique flags this process has ever seen, submitted or still held.
        "total_unique": len(seen) + len(pending),
        "submit": accepted[:300],
        "submit_error": err,
        "per_team": results,
    }
    if batch and not for_real:
        out["pending_note"] = ("nothing was submitted (dry run, or submit.url is "
                               "not set): these flags are held, not lost")
    if broken and len(broken) == len(results):
        # First key on purpose, and last thing built so it stays first. A wrong
        # interpreter path in the exploit argv otherwise reads as the entire
        # field patching within one tick, which is the single most misleading
        # thing this tool could print.
        out = {"ALERT": ("the exploit failed to run against every team; this is "
                         "a local problem"), **out}
    return out


def _load_set(path):
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as fh:
        return {line.strip() for line in fh if line.strip()}


def _save_set(path, values):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(sorted(values)))


def _load_int(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return int(fh.read().strip() or 0)
    except (OSError, ValueError):
        return 0


def _save_int(path, value):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(str(int(value)))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("config")
    ap.add_argument("--once", action="store_true", help="one tick and exit")
    ap.add_argument("--dry-run", action="store_true", help="run exploits, submit nothing")
    ap.add_argument("--state", default=None,
                    help="base path for the submitted-flag file; the held-flag file sits beside it with a .pending suffix")
    args = ap.parse_args()

    cfg = load_config(args.config)
    for warning in cfg.get("_warnings") or []:
        print(json.dumps({"warning": warning}), flush=True)

    base = args.state or (os.path.splitext(args.config)[0] + ".seen")
    seen_path = base
    # Held flags live beside the submitted ones, so a restart mid-outage still
    # retries instead of forgetting.
    pending_path = (base[:-5] if base.endswith(".seen") else base) + ".pending"
    # The consecutive-failure count is persisted too. The counter only works in
    # the long-running loop if it lives in memory, and a tick driven one at a
    # time with --once is a perfectly reasonable way to run this -- in which case
    # an in-memory counter resets to zero every tick and the ALERT never fires.
    fails_path = (base[:-5] if base.endswith(".seen") else base) + ".fails"
    seen = _load_set(seen_path)
    pending = _load_set(pending_path) - seen

    period = float(cfg.get("tick_seconds", 60))
    consecutive_failures = _load_int(fails_path)
    while True:
        start = time.monotonic()
        out = tick(cfg, seen, pending, args.dry_run)
        out["event"] = cfg["authorized_event"]

        if out["submit_error"]:
            consecutive_failures += 1
        elif out["submitted_ok"]:
            consecutive_failures = 0
        if consecutive_failures >= 3:
            # First key in the dict on purpose: this has to survive a scrolling
            # log, and a submission that has failed three ticks running is a
            # misconfigured submitter, not bad luck.
            alert = ("submission has failed for %d consecutive ticks; %d "
                     "flag(s) are pending. Check submit.method, submit.format and "
                     "the token against the rules NOW; the flags are held, not "
                     "lost." % (consecutive_failures, len(pending)))
            # tick() can already have raised its own alert about the exploit.
            # `{"ALERT": x, **out}` would drop it without a word, because the
            # later key wins -- so carry both, exploit first, since an exploit
            # that runs nowhere explains a submitter with nothing to send.
            if out.get("ALERT"):
                alert = out["ALERT"] + " ALSO: " + alert
            out = {"ALERT": alert,
                   **{k: v for k, v in out.items() if k != "ALERT"}}

        print(json.dumps(out, ensure_ascii=False), flush=True)
        _save_set(seen_path, seen)
        _save_set(pending_path, pending)
        _save_int(fails_path, consecutive_failures)

        if args.once:
            return 0
        slept = period - (time.monotonic() - start)
        if slept > 0:
            time.sleep(slept)


if __name__ == "__main__":
    sys.exit(main())
