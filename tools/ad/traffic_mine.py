#!/usr/bin/env python3
"""Find other teams' exploits in your own captured traffic, and replay them.

This is the highest-return move in attack-defense and the one this tree had no
tooling for. Every other team is attacking your service with a working exploit,
and their payloads arrive at your own network interface. Recovering one of those
is usually faster than finding the bug yourself, and it is immediately usable
against every other team, because everyone runs the same service.

    # capture first, with anything -- this tool does not sniff:
    #   tcpdump -i any -s0 -w cap.pcap 'tcp port 5000'
    #   tshark -r cap.pcap -q -z follow,tcp,ascii,0 > reqs/0.txt
    # or point a small proxy at a directory of raw request files.

    traffic_mine.py --baseline baseline/ --live live/ --top 10

`--baseline` is a directory of requests from the organiser's own checker, which
is the definition of "normal traffic" for this service. Everything in `--live`
is scored by how far it departs from that. Without a baseline every request
looks equally interesting, which is the same as having no signal.

Input files are raw HTTP requests as text -- request line, headers, blank line,
body -- one request per file, which is what tshark's follow output and most
tiny proxies produce.

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


def parse_request(text):
    """Split a raw HTTP request into its parts. Tolerant by design."""
    text = text.replace("\r\n", "\n")
    head, _, body = text.partition("\n\n")
    lines = [l for l in head.split("\n") if l.strip()]
    if not lines:
        return None
    m = re.match(r"([A-Z]+)\s+(\S+)\s+HTTP/", lines[0])
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
        for chunk in re.split(r"(?=^[A-Z]+ \S+ HTTP/)", text, flags=re.M):
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


def replay_template(req):
    """A curl the operator can point at any team by changing one variable."""
    parts = ["curl -sS -i --max-time 10"]
    if req["method"] != "GET":
        parts.append("-X %s" % req["method"])
    for k, v in (req["headers"] or {}).items():
        if k in ("host", "content-length", "connection", "accept-encoding"):
            continue
        parts.append("-H %s" % json.dumps("%s: %s" % (k, v)))
    if req["body"]:
        parts.append("--data-binary %s" % json.dumps(req["body"][:4000]))
    target = req["path"] + (("?" + req["query"]) if req["query"] else "")
    parts.append(json.dumps('http://$TARGET' + target))
    return " ".join(parts)


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--baseline", help="directory of known-good checker traffic")
    ap.add_argument("--live", required=True, help="directory of captured traffic to rank")
    ap.add_argument("--top", type=int, default=10)
    args = ap.parse_args()

    base_reqs = load_dir(args.baseline)
    live_reqs = load_dir(args.live)
    base = build_baseline(base_reqs)

    ranked = []
    for r in live_reqs:
        pts, reasons = score(r, base)
        if pts <= 0:
            continue
        ranked.append({
            "score": pts, "reasons": reasons, "file": r["_file"],
            "method": r["method"], "path": r["path"],
            "query": r["query"][:300], "body": (r["body"] or "")[:500],
            "replay": replay_template(r),
        })
    ranked.sort(key=lambda x: -x["score"])

    print(json.dumps({
        "mode": "traffic-mine",
        "baseline_requests": len(base_reqs),
        "live_requests": len(live_reqs),
        "baseline_paths": len(base["paths"]),
        "candidates": len(ranked),
        "note": ("with no baseline every request scores on payload shape alone, "
                 "which is far noisier -- capture the organiser's checker first"
                 if not base_reqs else ""),
        "top": ranked[:args.top],
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
