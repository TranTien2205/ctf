#!/usr/bin/env python3
"""Read Linux authentication evidence: auth.log text and wtmp/btmp binary records.

This is the artifact pair behind the canonical first Sherlock (Brutus) and behind
the only authentication evidence an attack-defense estate produces on its own
hosts. Nothing on this box parses either one: `last`, `utmpdump` and `lastb` read
the LIVE host's /var/run and /var/log, not a supplied artifact, and no Python
utmp module is installed here. So both parsers are stdlib and local.

Four traps this exists to remove, each of which has a wrong answer attached:

1. NO YEAR. A syslog line is `Mar  6 06:31:31 host sshd[2411]: ...` -- there is no
   year in the format at all. Any tool that silently assumes the current year
   produces a timestamp that is wrong by whole years, and it looks right. This
   tool never guesses: without --year the parsed date carries `year_assumed:
   null` and the ISO string is emitted with a `????` year so it cannot be pasted
   into an answer by accident. wtmp DOES carry a real epoch, so when both are
   supplied the wtmp record is what dates the session.
2. ROLLOVER. A log spanning New Year goes Dec 31 -> Jan 01, and ordering it by the
   month name alone puts January first. With --year, a month that goes backwards
   is treated as the next year and the count of such rollovers is reported.
3. THE WRONG "SESSION NUMBER". auth.log carries three different numbers that all
   read like a session id: the sshd PID in brackets, `Starting session: shell ...
   id 0`, and `systemd-logind: New session 37 of user root.` Only the last is the
   session number a question means. All three are extracted under distinct names
   so the answer is chosen rather than guessed.
4. A FAILURE COUNT IS NOT AN ATTACKER. The IP with the most failures is a
   candidate; the one that matters is the IP whose failures are followed by an
   ACCEPTANCE. --summary ranks by that join and states both numbers, so a noisy
   scanner is never mistaken for the successful one.

Timestamps from wtmp are UTC epoch seconds and are emitted as UTC. auth.log
timestamps are host-local with no offset recorded in the file; they are emitted
exactly as written plus a parsed form, and `timezone` is reported as `unknown`
rather than assumed, because a UTC answer read off a local-time log is the single
most common wrong answer in this category.

    python3 tools/forensics/linux_auth.py --authlog <auth.log> --summary \\
        --challenge <sherlock>-q1
    python3 tools/forensics/linux_auth.py --authlog <auth.log> --event accepted \\
        --challenge <sherlock>-q2 --answer user
    python3 tools/forensics/linux_auth.py --wtmp <wtmp> --event wtmp --ip 1.2.3.4 \\
        --challenge <sherlock>-q3 --answer time_utc
    python3 tools/forensics/linux_auth.py --authlog <auth.log> --event sudo \\
        --challenge <sherlock>-q8 --answer command
"""
import argparse
import os
import re
import struct
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fkit  # noqa: E402

# ---------------------------------------------------------------- wtmp / btmp
#
# struct utmp on Linux/x86_64, from utmp.h. Sizes are fixed by the ABI, not by
# the compiler's mood, but the 2 bytes of padding after ut_type are real and are
# encoded explicitly here because "<" turns off struct's own alignment.
#
#   short ut_type; (+2 pad)   int ut_pid;        char ut_line[32];
#   char  ut_id[4];           char ut_user[32];  char ut_host[256];
#   short e_termination; short e_exit;           int ut_session;
#   int tv_sec; int tv_usec;  int ut_addr_v6[4]; char unused[20]
UTMP = struct.Struct("<h2xi32s4s32s256shhiii4i20s")
UTMP_SIZE = 384
UT_TYPES = {0: "EMPTY", 1: "RUN_LVL", 2: "BOOT_TIME", 3: "NEW_TIME",
            4: "OLD_TIME", 5: "INIT_PROCESS", 6: "LOGIN_PROCESS",
            7: "USER_PROCESS", 8: "DEAD_PROCESS", 9: "ACCOUNTING"}


def _cstr(raw):
    """Bytes up to the first NUL, decoded leniently. Never raises on a artifact."""
    cut = raw.split(b"\x00", 1)[0]
    return cut.decode("utf-8", "replace")


def parse_wtmp(path):
    """Every utmp record in the file, plus what could not be read.

    A trailing partial record is COUNTED, not dropped: a truncated wtmp is itself
    a finding (a tail that was cut, or a file still being written), and silently
    discarding it hides exactly that.
    """
    records, problems = [], []
    try:
        with open(path, "rb") as fh:
            blob = fh.read()
    except OSError as exc:
        return [], ["unreadable: %s" % exc], 0
    whole, remainder = divmod(len(blob), UTMP_SIZE)
    if remainder:
        problems.append("%d trailing bytes are not a whole %d-byte record; the file "
                        "is truncated or is not utmp" % (remainder, UTMP_SIZE))
    for i in range(whole):
        chunk = blob[i * UTMP_SIZE:(i + 1) * UTMP_SIZE]
        try:
            (ut_type, pid, line, uid, user, host, term, exit_, session,
             sec, usec, a0, a1, a2, a3, _unused) = UTMP.unpack(chunk)
        except struct.error as exc:
            problems.append("record %d did not unpack: %s" % (i, exc))
            continue
        iso = ""
        if sec:
            iso = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(sec))
        records.append({
            "index": i,
            "ut_type": UT_TYPES.get(ut_type, "UNKNOWN(%d)" % ut_type),
            "pid": pid,
            "line": _cstr(line),
            "id": _cstr(uid),
            "user": _cstr(user),
            "host": _cstr(host),
            "session": session,
            "epoch": sec,
            "time_utc": iso,
            "exit": {"termination": term, "exit": exit_},
            # the raw record rendered as the one line a human reads, and the ONLY
            # string offered as evidence: it is built from the unpacked bytes, so
            # it cannot disagree with them
            "raw": "%s %s %s %s %s" % (iso or "(no time)",
                                       UT_TYPES.get(ut_type, ut_type),
                                       _cstr(user) or "-", _cstr(line) or "-",
                                       _cstr(host) or "-"),
        })
    return records, problems, whole


# ------------------------------------------------------------------- auth.log

SYSLOG = re.compile(
    r"^(?P<mon>[A-Z][a-z]{2})\s+(?P<day>\d{1,2})\s"
    r"(?P<time>\d{2}:\d{2}:\d{2})\s+(?P<host>\S+)\s+"
    r"(?P<prog>[^\s\[:]+)(?:\[(?P<pid>\d+)\])?:\s(?P<msg>.*)$")
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
     "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

# Each pattern names the fields it is allowed to claim. Anything not captured
# here stays absent from the record rather than being inferred from the text.
EVENTS = [
    ("failed", re.compile(
        r"Failed (?P<method>password|publickey|none) for (?:invalid user )?"
        r"(?P<user>\S+) from (?P<ip>\S+) port (?P<port>\d+)")),
    ("failed", re.compile(r"authentication failure;.*?ruser=.*?rhost=(?P<ip>\S+)"
                          r"(?:\s+user=(?P<user>\S+))?")),
    ("invalid-user", re.compile(r"Invalid user (?P<user>\S*) from (?P<ip>\S+)"
                                r"(?: port (?P<port>\d+))?")),
    ("accepted", re.compile(
        r"Accepted (?P<method>password|publickey|keyboard-interactive(?:/pam)?) for "
        r"(?P<user>\S+) from (?P<ip>\S+) port (?P<port>\d+)")),
    # the three numbers that all look like a session id, kept apart on purpose
    ("logind-session", re.compile(r"New session (?P<session>\d+) of user (?P<user>\S+?)\.?$")),
    ("sshd-session", re.compile(r"Starting session: (?P<shell>\S+)(?: on (?P<tty>\S+))?"
                                r" for (?P<user>\S+) from (?P<ip>\S+)"
                                r" port (?P<port>\d+) id (?P<id>\d+)")),
    ("pam-open", re.compile(r"session opened for user (?P<user>[^\s(]+)")),
    ("pam-close", re.compile(r"session closed for user (?P<user>\S+)")),
    ("disconnect", re.compile(r"(?:Disconnected from|Connection closed by)"
                             r"(?: (?:authenticating|invalid) user (?P<user>\S+))?"
                             r" (?P<ip>\d[\d.]+|[0-9a-f:]+) port (?P<port>\d+)")),
    ("sudo", re.compile(r"(?P<user>\S+)\s*:\s*TTY=(?P<tty>\S*)\s*;\s*PWD=(?P<pwd>\S*)\s*;"
                        r"\s*USER=(?P<target>\S*)\s*;\s*COMMAND=(?P<command>.*)$")),
    ("useradd", re.compile(r"new user: name=(?P<user>[^,]+), UID=(?P<uid>\d+),"
                           r" GID=(?P<gid>\d+), home=(?P<home>[^,]*)")),
    ("groupadd", re.compile(r"new group: name=(?P<group>[^,]+), GID=(?P<gid>\d+)")),
    ("group-member", re.compile(r"add '(?P<user>[^']+)' to group '(?P<group>[^']+)'")),
    ("password-change", re.compile(r"password changed for (?P<user>\S+)")),
]


def parse_authlog(path, year=None):
    """Classified auth.log records, with the no-year problem stated not solved."""
    records, problems = [], []
    unparsed = 0
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        return [], ["unreadable: %s" % exc], 0, 0
    rollovers = 0
    cur_year = year
    last_month = None
    for lineno, line in enumerate(lines, 1):
        if not line.strip():
            continue
        m = SYSLOG.match(line)
        if not m:
            unparsed += 1
            continue
        mon = MONTHS.get(m.group("mon"))
        # December -> January inside one file is a year rollover, and ordering by
        # month alone would put the January rows first.
        if year is not None and mon is not None:
            if last_month is not None and mon < last_month:
                cur_year += 1
                rollovers += 1
            last_month = mon
        stamp_raw = "%s %2s %s" % (m.group("mon"), m.group("day"), m.group("time"))
        if cur_year is not None and mon is not None:
            iso = "%04d-%02d-%02d %s" % (cur_year, mon, int(m.group("day")),
                                         m.group("time"))
        else:
            # deliberately unusable as an answer: no year exists in the source
            iso = "????-%02d-%02d %s" % (mon or 0, int(m.group("day")), m.group("time"))
        rec = {
            "lineno": lineno,
            "time_raw": stamp_raw,
            "time_parsed": iso,
            "year_assumed": cur_year,
            "timezone": "unknown: auth.log records no offset",
            "host": m.group("host"),
            "program": m.group("prog"),
            "pid": int(m.group("pid")) if m.group("pid") else None,
            "message": m.group("msg"),
            "event": "other",
            "raw": line,
        }
        for name, rx in EVENTS:
            hit = rx.search(m.group("msg"))
            if hit:
                rec["event"] = name
                for key, val in hit.groupdict().items():
                    if val is not None:
                        rec[key] = val
                break
        records.append(rec)
    if unparsed:
        problems.append("%d line(s) did not match the syslog format and were counted, "
                        "not dropped" % unparsed)
    if year is None and records:
        problems.append("no --year given: auth.log carries no year, so time_parsed "
                        "shows ???? and must not be used as an answer")
    return records, problems, unparsed, rollovers


# -------------------------------------------------------------------- summary

def bruteforce_summary(records):
    """Rank source addresses by the join that matters: failures THEN an acceptance.

    A count of failures alone ranks the loudest scanner first. The address that
    answers "who brute-forced this host successfully" is the one whose failures
    are followed by an Accepted line, so both numbers are reported and the
    ordering is on the join, never on the count.
    """
    by_ip = {}
    for rec in records:
        ip = rec.get("ip")
        if not ip:
            continue
        slot = by_ip.setdefault(ip, {
            "ip": ip, "failed": 0, "accepted": 0, "invalid_user": 0,
            "users_failed": {}, "users_accepted": [],
            "first_seen": rec["time_raw"], "last_seen": rec["time_raw"],
            "first_accepted_at": None, "first_accepted_line": None})
        slot["last_seen"] = rec["time_raw"]
        if rec["event"] == "failed":
            slot["failed"] += 1
            u = rec.get("user")
            if u:
                slot["users_failed"][u] = slot["users_failed"].get(u, 0) + 1
        elif rec["event"] == "invalid-user":
            slot["invalid_user"] += 1
        elif rec["event"] == "accepted":
            slot["accepted"] += 1
            if rec.get("user") and rec["user"] not in slot["users_accepted"]:
                slot["users_accepted"].append(rec["user"])
            if slot["first_accepted_at"] is None:
                slot["first_accepted_at"] = rec["time_raw"]
                slot["first_accepted_line"] = rec["raw"]
    out = []
    for slot in by_ip.values():
        slot["users_failed"] = sorted(slot["users_failed"].items(),
                                      key=lambda kv: -kv[1])[:8]
        slot["succeeded_after_failures"] = bool(slot["accepted"] and slot["failed"])
        out.append(slot)
    out.sort(key=lambda s: (0 if s["succeeded_after_failures"] else 1,
                            -s["failed"], -s["accepted"]))
    return out


def dotted(obj, path):
    cur = obj
    for part in path.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


# ----------------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        epilog="auth.log has no year and no timezone offset. wtmp has a real UTC "
               "epoch. When a question wants a UTC timestamp, the wtmp record is "
               "the artifact that can answer it.",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_argument_group("artifacts")
    src.add_argument("--authlog", action="append", default=[], metavar="PATH",
                     help="repeatable; a text auth.log / secure log")
    src.add_argument("--wtmp", action="append", default=[], metavar="PATH",
                     help="repeatable; a binary wtmp or btmp (384-byte utmp records)")
    src.add_argument("--year", type=int,
                     help="the year the auth.log covers. Without it no auth.log "
                          "timestamp is answerable, by design")

    f = ap.add_argument_group("filters")
    f.add_argument("--event", action="append", default=[], metavar="NAME",
                   help="repeatable: failed, accepted, invalid-user, sudo, useradd, "
                        "groupadd, group-member, logind-session, sshd-session, "
                        "pam-open, pam-close, disconnect, password-change, other, "
                        "or wtmp for utmp records")
    f.add_argument("--user", help="exact match on the record's user field")
    f.add_argument("--ip", help="exact match on the record's source address")
    f.add_argument("--contains", help="case-insensitive substring of the raw line")
    f.add_argument("--ut-type", help="utmp record type, e.g. USER_PROCESS")
    f.add_argument("--limit", type=int, default=20, help="records printed (default 20); "
                                                         "counts are over every match")
    f.add_argument("--order", choices=("asc", "desc"), default="asc")
    f.add_argument("--summary", action="store_true",
                   help="rank source addresses by failures followed by an acceptance")

    h = ap.add_argument_group("hooks.py argv")
    h.add_argument("--challenge", required=True, help="challenge name, as state.py knows it")
    h.add_argument("--class", dest="bug_class", metavar="BUG_CLASS")
    h.add_argument("--hypothesis-id")
    h.add_argument("--chain-card")
    h.add_argument("--evidence-kind", choices=fkit.EVIDENCE_KINDS, default="class",
                   help="class or impact are the only kinds that can confirm")
    h.add_argument("--on-match", choices=fkit.VERDICTS, default="inconclusive")
    h.add_argument("--on-miss", choices=fkit.VERDICTS, default="inconclusive")
    h.add_argument("--answer", metavar="FIELD",
                   help="field of the first match to emit the pre-flag argv for, "
                        "e.g. user, ip, command, session, time_utc")
    h.add_argument("--excerpt", type=int, default=400,
                   help="characters of the first matched record kept as evidence")
    ap.add_argument("--compact", action="store_true")
    a = ap.parse_args()

    if not a.authlog and not a.wtmp:
        ap.error("give at least one --authlog or --wtmp")

    sources, records, problems = [], [], []
    parsed_any = False

    for path in a.authlog:
        if not os.path.isfile(path):
            problems.append("missing auth.log: %s" % path)
            sources.append({"path": path, "kind": "authlog", "parsed": False,
                            "reason": "not a file"})
            continue
        recs, probs, unparsed, rollovers = parse_authlog(path, a.year)
        problems += ["%s: %s" % (os.path.basename(path), p) for p in probs]
        for r in recs:
            r["source"] = path
            r["artifact"] = "authlog"
        records += recs
        parsed_any = parsed_any or bool(recs)
        sources.append({"path": path, "kind": "authlog", "parsed": bool(recs),
                        "records": len(recs), "lines_unparsed": unparsed,
                        "year_rollovers": rollovers,
                        "year_assumed": a.year})

    for path in a.wtmp:
        if not os.path.isfile(path):
            problems.append("missing wtmp: %s" % path)
            sources.append({"path": path, "kind": "wtmp", "parsed": False,
                            "reason": "not a file"})
            continue
        recs, probs, whole = parse_wtmp(path)
        problems += ["%s: %s" % (os.path.basename(path), p) for p in probs]
        for r in recs:
            r["source"] = path
            r["artifact"] = "wtmp"
            r["event"] = "wtmp"
        records += recs
        parsed_any = parsed_any or bool(recs)
        sources.append({"path": path, "kind": "wtmp", "parsed": bool(recs),
                        "records": len(recs), "whole_records": whole})

    # ---- filter
    want = set(a.event)
    matched = []
    for rec in records:
        if want and rec.get("event") not in want:
            continue
        if a.user and rec.get("user") != a.user:
            continue
        if a.ip and rec.get("ip") != a.ip and rec.get("host") != a.ip:
            continue
        if a.ut_type and rec.get("ut_type") != a.ut_type:
            continue
        if a.contains and a.contains.lower() not in (rec.get("raw") or "").lower():
            continue
        matched.append(rec)

    # wtmp carries a real epoch; auth.log does not, so they cannot share one sort
    # key without inventing a date. Order each artifact on what it actually has.
    matched.sort(key=lambda r: (r.get("epoch") if r.get("epoch") is not None
                                else -1, r.get("time_raw") or "", r.get("lineno") or 0),
                 reverse=(a.order == "desc"))

    by_event = {}
    for rec in matched:
        by_event[rec.get("event")] = by_event.get(rec.get("event"), 0) + 1

    first = matched[0] if matched else None
    evidence = fkit.excerpt(first.get("raw") if first else "", a.excerpt)
    verdict, forced_kind, reasons = fkit.downgrade(
        a.on_match if matched else a.on_miss, bool(matched), parsed_any)
    kind = forced_kind or a.evidence_kind

    request = "linux_auth.py " + " ".join(
        ["--authlog %s" % p for p in a.authlog] +
        ["--wtmp %s" % p for p in a.wtmp] +
        (["--event %s" % e for e in a.event]) +
        (["--user %s" % a.user] if a.user else []) +
        (["--ip %s" % a.ip] if a.ip else []) +
        (["--contains %s" % a.contains] if a.contains else []))
    result = ("%d of %d record(s) matched across %d source(s)"
              % (len(matched), len(records), len(sources)))

    out = fkit.envelope(
        "linux-auth",
        ok=True,
        challenge=a.challenge,
        parser="stdlib: regex over syslog lines, struct over 384-byte utmp records",
        parser_ok=parsed_any,
        sources=sources,
        records_total=len(records),
        records_matched=len(matched),
        matched_by_event=by_event,
        proved_negative=(not matched and parsed_any),
        problems=problems,
        timezone_note=("auth.log timestamps are host-local with no offset in the "
                       "file and no year; wtmp timestamps are UTC epoch seconds"),
        records=matched[:a.limit] if a.limit else matched,
        verdict=verdict,
        evidence_kind=kind,
        evidence=evidence,
        verdict_downgrades=reasons,
    )
    if a.summary:
        out["address_ranking"] = bruteforce_summary(
            [r for r in records if r.get("artifact") == "authlog"])
        out["address_ranking_note"] = (
            "ordered by failures FOLLOWED BY an acceptance, then by failure count. "
            "succeeded_after_failures is the field that distinguishes the "
            "successful source from the loudest one")
    argv = fkit.post_probe_argv(a.challenge, verdict, evidence, kind, request,
                                result, a.bug_class, a.hypothesis_id, a.chain_card)
    out["post_probe_argv"] = argv
    out["post_probe_command"] = fkit.as_command(argv)
    if a.answer:
        if not first:
            out["answer"] = {"field": a.answer, "value": None,
                             "refused": "no record matched, so there is nothing to answer with"}
        else:
            value = dotted(first, a.answer)
            if value is None:
                out["answer"] = {"field": a.answer, "value": None,
                                 "refused": "the first matched record has no field %r; "
                                            "available: %s" % (a.answer,
                                                               sorted(first.keys()))}
            elif (a.answer in ("time_parsed",) and first.get("year_assumed") is None):
                out["answer"] = {
                    "field": a.answer, "value": str(value),
                    "refused": "auth.log carries no year, so this timestamp is not "
                               "answerable. Pass --year, or answer from the wtmp "
                               "record, which has a real UTC epoch"}
            else:
                out["answer"] = {"field": a.answer, "value": str(value)}
                out["pre_flag"] = fkit.as_command(
                    fkit.pre_flag_argv(a.challenge, str(value), evidence))
    fkit.jprint(out, a.compact)
    return 0


if __name__ == "__main__":
    sys.exit(main())
