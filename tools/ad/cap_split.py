#!/usr/bin/env python3
"""Split a capture into one raw HTTP REQUEST per file, client direction only.

`tools/ad/traffic_mine.py` eats raw HTTP requests, one request per file. The
pipeline its docstring used to suggest -- `tshark -q -z follow,tcp,ascii,<n>` --
emits BOTH directions plus a banner, so on a real two-stream capture the server's
response landed inside the parsed request body, response headers were counted as
parameter names, and a flag-shaped string out of the response travelled into the
replay command aimed at a third team. Measured, not assumed: 4 of 4 replay
commands carried the response, and the mined output held 11 occurrences of
`HTTP/1.0`. The operator would follow the tool's own documentation, get a curl
that POSTs the victim's response at someone else, get nothing back, and conclude
the bug is not there.

So this tool asks tshark for the request bytes as HEX and writes exactly those.

    dumpcap -i <iface> -q -f 'tcp port 5000' -a duration:60 -w cap.pcap
    python3 tools/ad/cap_split.py --pcap cap.pcap --out live/
    python3 tools/ad/traffic_mine.py --baseline baseline/ --live live/ --top 10

Why hex and not text. Three things were measured on tshark 4.0.7 here:

  * `-T fields` renders a real CR, LF or TAB inside a field as the two literal
    characters `\\r` `\\n` `\\t`, but passes a genuine backslash through unchanged.
    So a body of `{"p":"C:\\notes"}` is byte-identical to one holding an escaped
    newline, and no unescaping can be correct. Hex needs no unescaping at all.
  * on a request split across two TCP segments the `http.request` filter fires on
    the LAST frame, whose `tcp.payload` holds only the tail -- 58 bytes of a
    121-byte request in the measured case -- while `tcp.reassembled.data` holds
    the whole request. So reassembled data is preferred and payload is a fallback.
  * three requests pipelined on ONE keep-alive stream emit THREE rows, correctly
    separated. A `follow` dump of the same capture recovers an unknown fraction,
    because the number of streams is not knowable in advance: one measured capture
    put 4 requests on streams 0-3 and another put 3 requests on stream 0.

Output is JSON on stdout, like every other tool in this tree. `--from-fields`
reads a saved tshark run instead of shelling out: it is the escape hatch when
field names drift between tshark versions, and it is also the seam that lets
`tools/ad/selftest.py` prove this file with no tshark and no subprocess.
"""
import argparse
import binascii
import json
import os
import shutil
import subprocess
import sys

# One row per request. No field here can contain the "|" separator: three are
# numeric, one is an address, one is a method token and two are hex, which is
# what makes a plain split safe. A row with the wrong field count is reported as
# malformed rather than parsed into the wrong columns.
FIELDS = ("frame.number", "frame.time_epoch", "ip.src", "tcp.stream",
          "http.request.method", "tcp.reassembled.data", "tcp.payload")
SEPARATOR = "|"
AGGREGATOR = ","

METHODS = (b"GET", b"POST", b"PUT", b"DELETE", b"PATCH", b"HEAD", b"OPTIONS",
           b"TRACE", b"CONNECT")


def tshark_argv(pcap, display_filter):
    """The exact invocation. Kept as a function so the selftest can assert on it."""
    argv = ["tshark", "-r", pcap, "-Y", display_filter, "-T", "fields",
            "-E", "occurrence=a", "-E", "aggregator=" + AGGREGATOR,
            "-E", "separator=" + SEPARATOR]
    for f in FIELDS:
        argv += ["-e", f]
    return argv


def split_rows(text):
    """One list of fields per non-empty line.

    Never use str.splitlines() on tshark output: Python treats \\x1e and \\x85 as
    line boundaries, so a separator chosen from the ASCII control range shreds
    every row mid-field. This silently produced "rebuilt 0 requests" in a
    prototype run, so the split is explicit.
    """
    rows = []
    for line in text.split("\n"):
        line = line.rstrip("\r")
        if line.strip():
            rows.append(line.split(SEPARATOR))
    return rows


def rebuild(fields):
    """One row of fields -> the raw request bytes, or None if it is not one.

    Pure: no tshark, no filesystem. Prefers the reassembled stream data over the
    single frame's payload, because a request split across segments only has its
    tail in the payload.
    """
    if len(fields) != len(FIELDS):
        return None
    method = fields[4].strip()
    if not method:
        return None
    for candidate in (fields[5], fields[6]):
        hexed = candidate.strip()
        if not hexed:
            continue
        # Multiple occurrences arrive joined by the aggregator; take the first,
        # because concatenating them would duplicate retransmitted bytes.
        hexed = hexed.split(AGGREGATOR)[0].replace(":", "").strip()
        if not hexed or len(hexed) % 2:
            continue
        try:
            raw = binascii.unhexlify(hexed)
        except (binascii.Error, ValueError):
            continue
        if not any(raw.startswith(m) for m in METHODS):
            continue
        return raw
    return None


def strip_follow(text):
    """Salvage path: pull the client-direction requests out of a follow dump.

    Use `--pcap` instead whenever the capture still exists -- this cannot recover
    what the follow format threw away, it only refuses to pass the response on.
    A chunk is kept when it begins with an HTTP method; the banner and every
    server-direction chunk, which begins with `HTTP/`, are dropped.
    """
    out = []
    for chunk in text.split("\n\n"):
        body = chunk.lstrip()
        if not body or body.startswith("HTTP/"):
            continue
        first = body.split(None, 1)[0].encode()
        if first in METHODS:
            out.append(body)
    return out


def run_tshark(pcap, display_filter):
    """Shell out. Returns (stdout, version_line). Raises RuntimeError with JSON-able text."""
    if shutil.which("tshark") is None:
        raise RuntimeError("tshark is not installed; save a field run elsewhere "
                           "and pass it with --from-fields")
    version = ""
    try:
        v = subprocess.run(["tshark", "--version"], capture_output=True, timeout=20)
        version = v.stdout.decode("utf-8", "replace").split("\n")[0].strip()
    except Exception:
        version = "unknown"
    proc = subprocess.run(tshark_argv(pcap, display_filter),
                          capture_output=True, timeout=300)
    # tshark writes harmless WARNINGs to stderr on this box, e.g.
    # read_filter_list(): /usr/share/wireshark/cfilters line 1. A non-empty
    # stderr is NOT an error, and it must never be mixed into stdout.
    if proc.returncode != 0 and not proc.stdout.strip():
        raise RuntimeError("tshark exited %d: %s" % (
            proc.returncode, proc.stderr.decode("utf-8", "replace")[:400]))
    return proc.stdout.decode("utf-8", "replace"), version


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--pcap", help="capture to read with tshark")
    src.add_argument("--from-fields",
                     help="a saved tshark -T fields run, instead of shelling out")
    ap.add_argument("--out", required=True, help="directory to write one request per file")
    ap.add_argument("--port", type=int, help="only requests to this TCP port")
    ap.add_argument("--filter", help="a full tshark display filter, replacing the default")
    ap.add_argument("--append", action="store_true",
                    help="write into a directory that already holds files")
    ap.add_argument("--max-bytes", type=int, default=65536,
                    help="skip a request larger than this (default 65536)")
    ap.add_argument("--exclude-src", action="append", default=[],
                    help="drop requests from this source address; repeatable")
    ap.add_argument("--limit", type=int, help="stop after this many requests")
    args = ap.parse_args()

    if os.path.isdir(args.out) and os.listdir(args.out) and not args.append:
        print(json.dumps({
            "error": "the output directory is not empty",
            "out": args.out,
            "why": "mixing a baseline with live traffic destroys the only signal "
                   "traffic_mine has; write to a new directory, or pass --append"}))
        return 2

    display_filter = args.filter or "http.request"
    if args.port and not args.filter:
        display_filter = "http.request && tcp.port == %d" % args.port

    version = "not run (--from-fields)"
    if args.from_fields:
        try:
            with open(args.from_fields, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError as exc:
            print(json.dumps({"error": "cannot read the field file",
                              "detail": str(exc)}))
            return 2
    else:
        try:
            text, version = run_tshark(args.pcap, display_filter)
        except RuntimeError as exc:
            print(json.dumps({"error": str(exc), "fallback": "--from-fields"}))
            return 2
        except Exception as exc:
            print(json.dumps({"error": "%s: %s" % (type(exc).__name__, exc),
                              "fallback": "--from-fields"}))
            return 2

    rows = split_rows(text)
    records, skipped = [], 0
    for fields in rows:
        raw = rebuild(fields)
        if raw is None:
            skipped += 1
            continue
        if len(raw) > args.max_bytes:
            skipped += 1
            continue
        if fields[2].strip() in args.exclude_src:
            skipped += 1
            continue
        try:
            when = float(fields[1])
        except ValueError:
            when = 0.0
        records.append((when, fields[3].strip() or "0", fields[2].strip(), raw))

    records.sort(key=lambda r: r[0])
    if args.limit:
        records = records[:args.limit]

    os.makedirs(args.out, exist_ok=True)
    hosts, streams = set(), set()
    for seq, (_when, stream, src_ip, raw) in enumerate(records, 1):
        path = os.path.join(args.out, "%04d-s%s.txt" % (seq, stream))
        with open(path, "wb") as fh:
            fh.write(raw)
        hosts.add(src_ip)
        streams.add(stream)

    print(json.dumps({
        "mode": "cap-split",
        "pcap": args.pcap or args.from_fields,
        "out": args.out,
        "requests": len(records),
        "streams": len(streams),
        "skipped": skipped,
        # Printed so a field-name drift between tshark versions is visible here
        # rather than showing up as "0 requests" with no reason.
        "tshark": version,
        "hosts_seen": sorted(hosts),
        "next": "python3 tools/ad/traffic_mine.py --baseline <baseline-dir> "
                "--live %s --top 10" % args.out,
    }, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
