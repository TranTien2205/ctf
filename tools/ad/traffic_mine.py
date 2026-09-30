#!/usr/bin/env python3
"""Find other teams' exploits in your own captured traffic, and replay them.

This is the highest-return move in attack-defense and the one this tree had no
tooling for. Every other team is attacking your service with a working exploit,
and their payloads arrive at your own network interface. Recovering one of those
is usually faster than finding the bug yourself, and it is immediately usable
against every other team, because everyone runs the same service.

    # capture first -- this tool does not sniff. dumpcap, not tcpdump: on this
    # box /usr/bin/dumpcap carries cap_net_admin,cap_net_raw and tcpdump carries
    # none, so dumpcap needs no sudo. Always bound it with -a, or the disk fills.
    #   dumpcap -i <iface> -q -f 'tcp port 5000' -a duration:60 -w cap.pcap
    # then split it into one REQUEST per file:
    #   python3 tools/ad/cap_split.py --pcap cap.pcap --out live/

    traffic_mine.py --baseline baseline/ --live live/ --top 10

`--baseline` is a directory of requests from the organiser's own checker, which
is the definition of "normal traffic" for this service. Everything in `--live`
is scored by how far it departs from that. Without a baseline every request
looks equally interesting, which is the same as having no signal.

Input files are raw HTTP requests as text -- request line, headers, blank line,
body -- ONE REQUEST PER FILE, which is what `tools/ad/cap_split.py` produces.

Do not feed this `tshark -q -z follow,tcp,ascii,<n>`. That output holds both
directions plus a banner, and it was measured putting the server's response into
the parsed request body: the response headers were counted as parameter names and
a flag-shaped string out of the response travelled into the replay command aimed
at a third team. On one loopback capture, mining a follow dump produced 8
occurrences of `HTTP/1.0` in the output; the same capture through `cap_split.py`
produced 0. `cap_split.strip_follow()` is the salvage path when the capture is
already gone, and it can only drop the response, not recover what follow lost.

The replay command carries NO credentials. `Cookie`, `Authorization`,
`X-Team-Token` and five more identity headers are removed from it and NAMED in
`stripped_identity`. Keeping them is worse: the replay would either 401 against
a third team or authenticate you as the team whose request you copied, and their
bearer token would land in your shell history and in the scored write-up.
Removing them without saying so is worse again, because the 401 then reads as
"that team has already patched" and a live endpoint gets written off.

Two degraded inputs are accepted explicitly rather than guessed at:

  * a request line with LEADING WHITESPACE now parses. Measured before this
    change: `parse_request` returned None for both "  GET /a HTTP/1.1" and a
    tab-indented request line, so a request copied out of an indented log, a
    YAML block or a pasted transcript was dropped without a word.
  * `--live-access-log` and `--baseline-access-log` read a common or combined
    access log. This is the fallback for a containerised estate, a box with no
    root, and a host with no capture tooling -- there is nothing to capture with
    and the log is the only record of what arrived. It is a DEGRADED input: an
    access log records no request body and no request headers, so such a
    candidate carries method, path and query only, its score is a LOWER BOUND,
    and a payload that travelled in a POST body scores zero from it. Every
    candidate mined this way is marked `"source": "access-log"` and carries the
    list of what could not be recovered. Do not read a low score there as
    evidence that the request was benign.

Output is ranked JSON, with a ready-to-run replay template for each candidate.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
from collections import Counter

FLAGGY = re.compile(r"[A-Z0-9]{25,}=|flag\{|FLAG\{|HTB\{|[A-Za-z0-9+/]{40,}={0,2}")
SUSPECT = [
    (re.compile(r"\.\./|%2e%2e", re.I), "path traversal"),
    (re.compile(r"\bunion\b[\s\S]{0,40}\bselect\b", re.I), "sql union"),
    (re.compile(r"'\s*(or|and)\s*'?\d|\bor\b\s+1\s*=\s*1", re.I), "sql boolean"),
    (re.compile(r"\{\{|\$\{|<%="), "template injection"),
    (re.compile(r"__proto__|constructor\s*\[\s*[\"']prototype"), "prototype pollution"),
    (re.compile(r";\s*(cat|ls|id|sh|bash|curl|wget)\b|\|\s*(sh|bash)\b"), "command injection"),
    (re.compile(r"<script|onerror\s*=|javascript:", re.I), "xss"),
    (re.compile(r"\$ne\b|\$regex\b|\$where\b"), "nosql operator"),
    # Text-visible markers only. The raw Java magic bytes AC ED 00 05 are not
    # usable here: the capture is decoded with errors="replace", so those bytes
    # arrive as U+FFFD and can never match. rO0AB is the same header in base64,
    # which is the form it actually travels in over HTTP.
    (re.compile(r"\bpickle\b|rO0AB|O:\d+:\"|gASV"), "deserialization"),
    (re.compile(r"%00|\x00"), "null byte"),
]

# Two groups, dropped for two different reasons, which is why they are not one
# list. TRANSPORT describes the connection the request was captured on and is
# meaningless on a new one; dropping it silently is correct. IDENTITY
# authenticates the ATTACKING team, and dropping it silently is how the
# highest-return move in attack-defense stops working without telling anyone:
# the replay 401s against a third team, the operator writes that team down as
# immune, and the cause is a session header nobody saw leave. So IDENTITY is
# dropped AND named.
TRANSPORT_HEADERS = frozenset((
    "host", "content-length", "connection", "accept-encoding",
    "keep-alive", "te", "transfer-encoding", "upgrade", "expect",
))
IDENTITY_HEADERS = frozenset((
    "cookie", "authorization", "x-team-token", "x-api-key", "x-auth-token",
    "proxy-authorization", "x-csrf-token", "x-xsrf-token",
))

REPLAY_NOTE_AUTH = ("this request was authenticated as the ATTACKING team; the "
                    "replay will 401 until you substitute your own credential "
                    "for the target.")
REPLAY_NOTE_CLEAN = ("no credential-bearing header was present, so the replay "
                     "reproduces the captured request in full.")
REPLAY_NOTE_ACCESS_LOG = ("recovered from an access log, which records no "
                          "request body and no request headers: this replay "
                          "carries the method, the path and the query only. A "
                          "POST or PUT will not reproduce until you supply its "
                          "body yourself.")

# A common or combined line. The quoted request field is captured whole and
# parsed separately, so a log that records "-" or a malformed request verbatim
# is reported as unparsed instead of being forced into the wrong columns. There
# is deliberately no end anchor: nginx operators routinely append $request_time
# or an upstream address, and a line with extra trailing fields is still a
# usable record of what arrived.
ACCESS_LOG_RE = re.compile(
    r'^\s*(?P<client>\S+)\s+(?P<ident>\S+)\s+(?P<user>\S+)\s+'
    r'\[(?P<time>[^\]]*)\]\s+'
    r'"(?P<request>[^"]*)"\s+'
    r'(?P<status>\d{3})\s+(?P<size>-|\d+)'
    r'(?:\s+"(?P<referer>[^"]*)"\s+"(?P<agent>[^"]*)")?'
)
ACCESS_LOG_REQUEST_RE = re.compile(r'^([A-Z]+)\s+(\S+)(?:\s+HTTP/[\d.]+)?$')

# Stated on every access-log candidate. The scorer reads body and headers, and
# an access log has neither, so silence here would let an undercount read as a
# measurement.
ACCESS_LOG_UNRECOVERABLE = (
    "request body",
    "request headers other than user-agent and referer",
    "cookies, authorization and any other credential",
)
ACCESS_LOG_SCORE_NOTE = (
    "access-log candidates carry no body and no headers, so their score is a "
    "LOWER BOUND -- a payload that travelled in a POST body scores zero here. "
    "A low score on an access-log candidate is not evidence that the request "
    "was benign."
)
# A log file can be gigabytes. Bounded on purpose: an unbounded read is how a
# triage tool takes the box down while you are reading its output.
ACCESS_LOG_MAX_LINES = 200000


def parse_request(text):
    """Split a raw HTTP request into its parts. Tolerant by design."""
    text = text.replace("\r\n", "\n")
    head, _, body = text.partition("\n\n")
    lines = [l for l in head.split("\n") if l.strip()]
    if not lines:
        return None
    # lstrip first: re.match anchors at position 0, so before this a request
    # line indented by two spaces or one tab returned None and the request was
    # dropped without a word. Both were measured returning None.
    m = re.match(r"([A-Z]+)\s+(\S+)\s+HTTP/", lines[0].lstrip())
    if not m:
        return None
    method, target = m.group(1), m.group(2)
    path, _, query = target.partition("?")
    headers = {}
    for line in lines[1:]:
        k, _, v = line.partition(":")
        if v:
            headers[k.strip().lower()] = v.strip()
    return {"method": method, "path": path, "query": query,
            "headers": headers, "body": body}


def parse_access_log_line(line):
    """One common or combined access-log line -> the shape the scorer reads.

    This is the hedge for an estate with nothing to capture with: a container
    with no NET_ADMIN, a box with no root, a host with no capture tooling. The
    log is then the only record of what other teams sent.

    It is NOT a raw request and the returned dict says so. An access log records
    the method, the target and the response status; it does not record the
    request body, and of the request headers it records only User-Agent and
    Referer, and only in the combined format. So `body` is empty and `headers`
    holds at most those two. `_source`, `_recovered` and `_unrecoverable` are on
    the dict so a caller cannot mistake this for a full request: score() reads
    body and headers, and a body-only payload scores zero from a log line.

    Returns None -- never a half-filled dict -- when the line is not a log line
    in this format, or when the quoted request field is "-" or malformed, which
    is what a server writes for a request it could not parse. A log that escapes
    a quote inside that field (Apache writes \\", nginx writes \\x22) will not
    match; that is reported as unparsed rather than mis-split.
    """
    m = ACCESS_LOG_RE.match(line)
    if not m:
        return None
    rm = ACCESS_LOG_REQUEST_RE.match(m.group("request").strip())
    if not rm:
        return None
    method, target = rm.group(1), rm.group(2)
    # A proxy logs the absolute form. Left alone it would build the replay URL
    # "http://$TARGEThttp://victim/path", which resolves to nothing.
    for scheme in ("http://", "https://"):
        if target.lower().startswith(scheme):
            rest = target[len(scheme):]
            slash = rest.find("/")
            target = rest[slash:] if slash >= 0 else "/"
            break
    path, _, query = target.partition("?")

    headers = {}
    recovered = ["method", "path", "query", "status", "client", "time"]
    referer, agent = m.group("referer"), m.group("agent")
    if agent and agent != "-":
        headers["user-agent"] = agent
        recovered.append("user-agent")
    if referer and referer != "-":
        headers["referer"] = referer
        recovered.append("referer")
    try:
        status = int(m.group("status"))
    except (TypeError, ValueError):
        status = None
    return {
        "method": method, "path": path, "query": query,
        "headers": headers, "body": "",
        "status": status,
        "client": m.group("client"),
        "log_time": m.group("time"),
        "_source": "access-log",
        "_recovered": recovered,
        "_unrecoverable": list(ACCESS_LOG_UNRECOVERABLE),
    }


def parse_access_log(text, name="access-log"):
    """Text of an access log -> {"requests": [...], "unparsed": N}.

    `unparsed` is reported rather than swallowed: a log in a format this adapter
    does not read would otherwise produce an empty candidate list, which looks
    exactly like "nobody attacked us".
    """
    reqs, unparsed = [], 0
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        req = parse_access_log_line(line)
        if req is None:
            unparsed += 1
            continue
        req["_file"] = "%s:%d" % (name, n)
        reqs.append(req)
    return {"requests": reqs, "unparsed": unparsed}


def load_access_log(path):
    """Read one access log, or every file in a directory of them.

    Bounded at ACCESS_LOG_MAX_LINES per file and it says when it truncated, so
    a rotated multi-gigabyte log cannot turn triage into an outage.
    """
    out = {"requests": [], "unparsed": 0, "files": [], "truncated": []}
    if not path:
        return out
    if os.path.isdir(path):
        names = [os.path.join(path, n) for n in sorted(os.listdir(path))]
    else:
        names = [path]
    for full in names:
        if not os.path.isfile(full):
            continue
        lines = []
        try:
            with open(full, encoding="utf-8", errors="replace") as fh:
                for n, line in enumerate(fh):
                    if n >= ACCESS_LOG_MAX_LINES:
                        out["truncated"].append(os.path.basename(full))
                        break
                    lines.append(line)
        except OSError:
            continue
        got = parse_access_log("".join(lines), os.path.basename(full))
        out["requests"] += got["requests"]
        out["unparsed"] += got["unparsed"]
        out["files"].append(os.path.basename(full))
    return out


def load_dir(path):
    out = []
    if not path or not os.path.isdir(path):
        return out
    for name in sorted(os.listdir(path)):
        full = os.path.join(path, name)
        if not os.path.isfile(full):
            continue
        try:
            with open(full, encoding="utf-8", errors="replace") as fh:
                text = fh.read(200000)
        except OSError:
            continue
        # One file may hold several requests concatenated by a follow stream.
        # [ \t]* for the same reason parse_request lstrips: without it a file
        # of indented requests is one unsplit blob and only the first parses.
        for chunk in re.split(r"(?=^[ \t]*[A-Z]+ \S+ HTTP/)", text, flags=re.M):
            req = parse_request(chunk)
            if req:
                req["_file"] = name
                out.append(req)
    return out


def param_names(req):
    names = set(urllib.parse.parse_qs(req["query"]).keys())
    body = req["body"] or ""
    if "=" in body and "{" not in body[:2]:
        names |= set(urllib.parse.parse_qs(body).keys())
    if body.strip().startswith("{"):
        try:
            obj = json.loads(body)
            if isinstance(obj, dict):
                names |= set(obj.keys())
        except ValueError:
            pass
    return names


def build_baseline(reqs):
    return {
        "paths": Counter(r["path"] for r in reqs),
        "params": Counter(p for r in reqs for p in param_names(r)),
        "methods": Counter(r["method"] for r in reqs),
    }


def score(req, base):
    """Higher is more interesting. Each reason is a separate, statable fact."""
    reasons, points = [], 0
    if req["path"] not in base["paths"]:
        points += 3
        reasons.append("path %s never appears in the baseline" % req["path"])
    unseen = sorted(p for p in param_names(req) if p not in base["params"])
    if unseen:
        points += 2 * len(unseen)
        reasons.append("parameters not in the baseline: " + ", ".join(unseen[:6]))
    if req["method"] not in base["methods"]:
        points += 2
        reasons.append("method %s never appears in the baseline" % req["method"])

    # Scan the PATH as well as the query and body: traversal and a lot of
    # framework-specific injection live in the path, not in a parameter.
    # And scan the URL-DECODED form too -- an attacker's payload arrives as
    # id=1'%20OR%201=1--, where %20 is not whitespace, so a pattern written
    # with \s+ never fires against the raw bytes.
    raw = "\n".join([req["path"], req["query"], req["body"] or ""])
    try:
        decoded = urllib.parse.unquote_plus(raw)
    except Exception:
        decoded = raw
    blob = raw + "\n" + decoded
    for rx, label in SUSPECT:
        if rx.search(blob):
            points += 4
            reasons.append("payload looks like %s" % label)
    if FLAGGY.search(blob):
        points += 1
        reasons.append("carries a flag-shaped or long encoded value")
    # A very long body is how a serialized or chained payload usually shows up.
    if len(req["body"] or "") > 2000:
        points += 1
        reasons.append("unusually long body (%d bytes)" % len(req["body"]))
    return points, reasons


def replay_plan(req):
    """A curl the operator can point at any team, plus what was taken out of it.

    Returns {"curl", "stripped_identity", "needs_auth", "note"}. The stripping
    is in the return value rather than in a comment because an operator who does
    not know a session header was dropped will not know to add their own: the
    replay 401s against a third team, that team goes down as immune, and the
    highest-return move in attack-defense quietly stops working for every
    authenticated endpoint -- which is most of them.

    Keeping the header instead is worse in both directions: the replay would
    either 401 anyway or authenticate you as the team whose request you copied,
    and their bearer token would land in your shell history and in the scored
    write-up, against this tree's rule on committing credentials.
    """
    # --path-as-is, from `curl --help all` on this box: "Do not squash ..
    # sequences in URL path". Without it curl normalises the path before
    # sending, so a traversal candidate -- 4 points in score() and one of the
    # highest-value shapes here -- replays as a clean 404 and gets discarded.
    parts = ["curl -sS -i --path-as-is --max-time 10"]
    if req["method"] != "GET":
        parts.append("-X %s" % req["method"])
    stripped = []
    for k, v in (req.get("headers") or {}).items():
        if k in TRANSPORT_HEADERS:
            continue
        if k in IDENTITY_HEADERS:
            stripped.append(k)
            continue
        parts.append("-H %s" % json.dumps("%s: %s" % (k, v)))
    if req.get("body"):
        parts.append("--data-binary %s" % json.dumps(req["body"][:4000]))
    target = req["path"] + (("?" + req["query"]) if req["query"] else "")
    parts.append(json.dumps('http://$TARGET' + target))

    stripped = sorted(stripped)
    if req.get("_source") == "access-log":
        note = REPLAY_NOTE_ACCESS_LOG
    elif stripped:
        note = REPLAY_NOTE_AUTH
    else:
        note = REPLAY_NOTE_CLEAN
    return {"curl": " ".join(parts), "stripped_identity": stripped,
            "needs_auth": bool(stripped), "note": note}


def replay_template(req):
    """The replay command on its own, as a string.

    replay_plan() is the whole answer. This stays a str because callers already
    read it as one -- the `replay` field of this tool's JSON and three cases in
    tools/ad/selftest.py -- and a caller that treats a dict as a command string
    fails in a way nothing here would catch.
    """
    return replay_plan(req)["curl"]


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", help="directory of known-good checker traffic")
    ap.add_argument("--live", help="directory of captured raw requests to rank")
    # --live is no longer required=True because an estate with nothing to
    # capture with has no such directory at all. argparse would then refuse the
    # only invocation that works there.
    ap.add_argument("--baseline-access-log",
                    help="common/combined access log (file or directory) to use "
                         "as the baseline instead of, or as well as, --baseline")
    ap.add_argument("--live-access-log",
                    help="common/combined access log (file or directory) to rank. "
                         "DEGRADED input: no body and no headers are recorded, so "
                         "scores from it are a lower bound")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    if not args.live and not args.live_access_log:
        ap.error("nothing to rank: pass --live <dir of raw requests> or "
                 "--live-access-log <file or dir>")

    base_reqs = load_dir(args.baseline)
    live_reqs = load_dir(args.live)
    base_log = load_access_log(args.baseline_access_log)
    live_log = load_access_log(args.live_access_log)
    base_reqs += base_log["requests"]
    live_reqs += live_log["requests"]
    base = build_baseline(base_reqs)

    ranked = []
    for r in live_reqs:
        pts, reasons = score(r, base)
        if pts <= 0:
            continue
        rep = replay_plan(r)
        entry = {
            "score": pts, "reasons": reasons, "file": r["_file"],
            "source": r.get("_source", "raw-request"),
            "method": r["method"], "path": r["path"],
            "query": r["query"][:300], "body": (r["body"] or "")[:500],
            # `replay` stays the command STRING it has always been; the two keys
            # beside it are what used to be silent.
            "replay": rep["curl"],
            "stripped_identity": rep["stripped_identity"],
            "replay_needs_auth": rep["needs_auth"],
            "replay_note": rep["note"],
        }
        if r.get("_source") == "access-log":
            entry["unrecoverable"] = r["_unrecoverable"]
        ranked.append(entry)
    ranked.sort(key=lambda x: -x["score"])

    out = {
        "mode": "traffic-mine",
        "baseline_requests": len(base_reqs),
        "live_requests": len(live_reqs),
        "baseline_paths": len(base["paths"]),
        "candidates": len(ranked),
        "note": ("with no baseline every request scores on payload shape alone, "
                 "which is far noisier -- capture the organiser's checker first"
                 if not base_reqs else ""),
    }
    if args.live_access_log or args.baseline_access_log:
        # Reported whenever an access log was read at all, including when it
        # yielded nothing: an unreadable log format and a quiet network look
        # identical in a candidate count.
        out["access_log"] = {
            "live_requests": len(live_log["requests"]),
            "baseline_requests": len(base_log["requests"]),
            "unparsed_lines": live_log["unparsed"] + base_log["unparsed"],
            "files": live_log["files"] + base_log["files"],
            "truncated_at_%d_lines" % ACCESS_LOG_MAX_LINES:
                live_log["truncated"] + base_log["truncated"],
            "not_recoverable": list(ACCESS_LOG_UNRECOVERABLE),
            "note": ACCESS_LOG_SCORE_NOTE,
        }
    out["top"] = ranked[:args.top]
    print(json.dumps(out, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
