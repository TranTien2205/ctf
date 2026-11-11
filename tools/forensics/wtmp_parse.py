#!/usr/bin/env python3
"""wtmp_parse.py -- decode utmp/wtmp/btmp login records (last -f fallback).

Usage:
  python3 tools/forensics/wtmp_parse.py wtmp
  python3 tools/forensics/wtmp_parse.py btmp --type DEAD,LOGIN
  python3 tools/forensics/wtmp_parse.py lastlog --lastlog
  python3 tools/forensics/wtmp_parse.py --selftest

utmp record is 384 bytes on Linux/glibc: ut_type i32 @0
(EMPTY 0, RUN_LVL 1, BOOT_TIME 2, NEW_TIME 3, OLD_TIME 4,
INIT_PROCESS 5, LOGIN_PROCESS 6, USER_PROCESS 7, DEAD_PROCESS 8,
ACCOUNTING 9), pid @4, ut_line char[32] @8, ut_id char[4] @40,
ut_user char[32] @44, ut_host char[256] @76, exit_status i16+i16
@332, session i32 @336, tv_sec+tv_usec i32 @340, addr_v6 i32[4]
@348, unused @364. wtmp = successful logins/logouts, btmp = failed
attempts only (usually DEAD/LOGIN lines with the tried username).
"""
import argparse
import json
import struct
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RECSZ = 384
TYPES = {
    0: "EMPTY", 1: "RUN_LVL", 2: "BOOT_TIME", 3: "NEW_TIME",
    4: "OLD_TIME", 5: "INIT_PROCESS", 6: "LOGIN_PROCESS",
    7: "USER_PROCESS", 8: "DEAD_PROCESS", 9: "ACCOUNTING",
}


def _s(b):
    return b.split(b"\x00")[0].decode("ascii", "replace")


def records(d):
    out = []
    for i in range(0, len(d) - RECSZ + 1, RECSZ):
        r = d[i:i + RECSZ]
        t = struct.unpack("<i", r[0:4])[0]
        if t < 0 or t > 9:
            continue                      # not aligned / not utmp
        sec, usec = struct.unpack("<ii", r[340:348])
        ip = struct.unpack("<4i", r[348:364])
        out.append({
            "offset": i, "type": TYPES.get(t, str(t)),
            "pid": struct.unpack("<i", r[4:8])[0],
            "line": _s(r[8:40]), "id": _s(r[40:44]),
            "user": _s(r[44:76]), "host": _s(r[76:332]),
            "exit": list(struct.unpack("<hh", r[332:336])),
            "session": struct.unpack("<i", r[336:340])[0],
            "time": datetime.fromtimestamp(sec, timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%S") if 0 < sec < 2**31
            else None,
            "tv_usec": usec,
            "ip": ".".join(str(x & 0xFF) for x in ip)
            if any(ip) else None})
    return out


def _selftest():
    def rec(t, pid, line, user, host, sec, ip=(0, 0, 0, 0)):
        r = bytearray(RECSZ)
        struct.pack_into("<i", r, 0, t)
        struct.pack_into("<i", r, 4, pid)
        r[8:8 + len(line)] = line
        r[40:44] = b"ts/1"
        r[44:44 + len(user)] = user
        r[76:76 + len(host)] = host
        struct.pack_into("<i", r, 336, 4242)
        struct.pack_into("<ii", r, 340, sec, 0)
        struct.pack_into("<4i", r, 348, *ip)
        return bytes(r)
    d = (rec(2, 0, b"", b"reboot", b"6.1.0-amd64", 1700000000)
         + rec(7, 100, b"pts/1", b"root", b"10.0.0.5",
               1700000060, (10, 0, 0, 5))
         + rec(8, 100, b"pts/1", b"", b"", 1700000900)
         + rec(6, 200, b"pts/2", b"LOGIN", b"", 1700001000))
    rs = records(d)
    assert len(rs) == 4, rs
    assert rs[1]["type"] == "USER_PROCESS" and rs[1]["user"] == "root"
    assert rs[1]["time"] == "2023-11-14T22:14:20", rs[1]["time"]
    assert rs[1]["ip"] == "10.0.0.5", rs[1]["ip"]
    assert rs[2]["type"] == "DEAD_PROCESS" and rs[2]["user"] == ""
    assert rs[3]["type"] == "LOGIN_PROCESS"
    # lastlog: 292-byte records indexed by uid
    ll = bytearray(292 * 3)
    struct.pack_into("<i", ll, 292, 1700000060)
    ll[292 + 4:292 + 9] = b"pts/9"
    ll[292 + 36:292 + 45] = b"evil.host"
    ls = lastlog_records(bytes(ll))
    assert len(ls) == 1 and ls[0]["uid"] == 1, ls
    assert ls[0]["line"] == "pts/9" and ls[0]["host"] == "evil.host"
    print("wtmp_parse selftest: ok")


def lastlog_records(d):
    """lastlog: one 292B record per uid - i32 time, line[32], host[256]."""
    out = []
    for uid, off in enumerate(range(0, len(d) - 291, 292)):
        r = d[off:off + 292]
        sec = struct.unpack("<i", r[0:4])[0]
        if sec <= 0:
            continue
        out.append({
            "uid": uid,
            "time": datetime.fromtimestamp(sec, timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%S"),
            "line": _s(r[4:36]), "host": _s(r[36:292])})
    return out


def main():
    ap = argparse.ArgumentParser(
        description="decode utmp/wtmp/btmp records")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--type", help="comma list, e.g. USER_PROCESS,DEAD_PROCESS")
    ap.add_argument("--lastlog", action="store_true",
                    help="parse as lastlog (292B records indexed by uid)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    d = Path(a.file).read_bytes()
    if a.lastlog:
        rs = lastlog_records(d)
    else:
        rs = records(d)
    if a.type:
        want = {t.strip().upper() for t in a.type.split(",")}
        rs = [r for r in rs if r["type"] in want]
    print(json.dumps({"records": rs, "total": len(rs)}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
