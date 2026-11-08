#!/usr/bin/env python3
r"""log_summary.py — bracket, count, distribute for forensics-log-analysis.

The class's probe order is fixed: wc -l + head/tail to bracket the
timeframe, then a field distribution, then the question grep. This does
the first two without awk on the box: `summary` reports line count,
first/last lines, detected timestamp range, per-hour histogram, and
top-N counts of the fields that matter (IPs, user names, paths, status
codes); `field` runs a custom column or regex distribution; `window`
prints context around a hit line. All reads are local; the verbatim
lines stay the evidence.

    python3 tools/log_summary.py summary access.log
    python3 tools/log_summary.py field auth.log --regex 'for (\w+) from'
    python3 tools/log_summary.py window app.log --around 1234 --ctx 3
    python3 tools/log_summary.py --selftest
"""
from __future__ import annotations

import argparse
import gzip
import json
import re
import sys
from collections import Counter

_TS_RX = [
    re.compile(r"^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})"),           # syslog
    re.compile(r"\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2})"),      # apache
    re.compile(r"(\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2})"),     # iso
    re.compile(r"(\d{2}/\w{3}/\d{4}\s+\d{2}:\d{2}:\d{2})"),      # other
]
_IP_RX = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
_USER_RX = re.compile(r"(?:for|user[ =:])([A-Za-z0-9_.-]+)", re.I)
_PATH_RX = re.compile(r'"[A-Z]+ ([^ ?"]+)')
_STATUS_RX = re.compile(r'" (\d{3}) ')
_FLAG_RX = re.compile(r"flag|ctf\{", re.I)


def _read(path, max_lines=2_000_000):
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt", errors="replace") as fh:
        for i, line in enumerate(fh):
            if i >= max_lines:
                break
            out.append(line.rstrip("\n"))
    return out


def _ts(line):
    for rx in _TS_RX:
        m = rx.search(line)
        if m:
            return m.group(1)
    return None


def _hour(ts):
    for fmt in ("%b %d %H:%M:%S", "%d/%b/%Y:%H:%M:%S",
                "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S",
                "%d/%b/%Y %H:%M:%S"):
        try:
            import datetime
            t = datetime.datetime.strptime(ts, fmt)
            return t.strftime("%Y-%m-%d %H:00")
        except ValueError:
            continue
    return ts[:13]


def cmd_summary(args):
    lines = _read(args.file)
    tss = [_ts(l) for l in lines]
    tss = [t for t in tss if t]
    ips = Counter()
    users = Counter()
    paths = Counter()
    codes = Counter()
    for l in lines:
        ips.update(_IP_RX.findall(l))
        users.update(_USER_RX.findall(l))
        m = _PATH_RX.search(l)
        if m:
            paths.update([m.group(1)])
        m = _STATUS_RX.search(l)
        if m:
            codes.update([m.group(1)])
    flagged = [i for i, l in enumerate(lines) if _FLAG_RX.search(l)][:10]
    out = {
        "file": args.file, "lines": len(lines),
        "first_line": lines[0][:200] if lines else None,
        "last_line": lines[-1][:200] if lines else None,
        "ts_first": tss[0] if tss else None,
        "ts_last": tss[-1] if tss else None,
        "per_hour": dict(sorted(
            Counter(_hour(t) for t in tss).items())) if tss else {},
        "top_ips": ips.most_common(10),
        "top_users": users.most_common(10),
        "top_paths": paths.most_common(10),
        "status_codes": codes.most_common(10),
        "flag_like_lines": [{"line": i + 1, "text": lines[i][:200]}
                            for i in flagged],
    }
    print(json.dumps(out, indent=1))
    return 0


def cmd_field(args):
    lines = _read(args.file)
    c = Counter()
    rx = re.compile(args.regex) if args.regex else None
    for l in lines:
        if rx:
            m = rx.search(l)
            if m:
                c.update([m.group(1) if m.groups() else m.group(0)])
        elif args.col is not None:
            parts = l.split()
            if args.col < len(parts):
                c.update([parts[args.col]])
    print(json.dumps({"file": args.file, "distinct": len(c),
                      "top": c.most_common(args.top)}, indent=1))
    return 0


def cmd_window(args):
    lines = _read(args.file)
    i = args.around - 1
    lo, hi = max(0, i - args.ctx), min(len(lines), i + args.ctx + 1)
    print("\n".join(f"{n + 1}: {lines[n]}" for n in range(lo, hi)))
    return 0


def _selftest() -> int:
    import tempfile, os
    data = "\n".join(
        ["127.0.0.1 - - [10/Oct/2024:13:55:01 +0000] \"GET /a HTTP/1.1\" 200 5",
         "8.8.8.8 - - [10/Oct/2024:13:55:02 +0000] \"GET /b HTTP/1.1\" 404 2",
         "127.0.0.1 - - [10/Oct/2024:13:55:03 +0000] \"GET /flag HTTP/1.1\" 200 9",
         "8.8.8.8 - - [10/Oct/2024:13:55:04 +0000] \"POST /login HTTP/1.1\" 403 2"]
    )
    with tempfile.NamedTemporaryFile("w", suffix=".log", delete=False) as fh:
        fh.write(data)
        path = fh.name
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        cmd_summary(argparse.Namespace(file=path))
    out = json.loads(buf.getvalue())
    os.unlink(path)
    assert out["lines"] == 4 and out["top_ips"][0][0] in ("127.0.0.1", "8.8.8.8"), out
    assert out["flag_like_lines"] and "/flag" in out["flag_like_lines"][0]["text"], out
    assert any("/a" == p for p, _ in out["top_paths"]), out
    print("log_summary selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("summary"); s.add_argument("file")
    s.set_defaults(fn=cmd_summary)
    f = sub.add_parser("field"); f.add_argument("file")
    f.add_argument("--col", type=int); f.add_argument("--regex")
    f.add_argument("--top", type=int, default=20)
    f.set_defaults(fn=cmd_field)
    w = sub.add_parser("window"); w.add_argument("file")
    w.add_argument("--around", type=int, required=True)
    w.add_argument("--ctx", type=int, default=3)
    w.set_defaults(fn=cmd_window)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if getattr(args, "fn", None):
        return args.fn(args)
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
