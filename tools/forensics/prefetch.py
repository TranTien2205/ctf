#!/usr/bin/env python3
"""prefetch.py -- read a Windows .pf prefetch file (uncompressed).

Usage:
  python3 tools/forensics/prefetch.py FILE.pf
  python3 tools/forensics/prefetch.py --selftest

Layout: version(4: 0x11 XP, 0x17 Win7, 0x1A Win8, 0x1E Win10,
0x1F Win11) + "SCCA"(4) + utf16 filename at 16 (up to 60 chars) +
version-dependent run count and last-run FILETIME slots. Windows 8+
files keep EIGHT execution timestamps at 0x80; Windows 7 and earlier
keep exactly one at 0x78 - the difference answers "was it run more
than once". MAM-compressed bodies (Win10+) are reported honestly as
compressed rather than misread.
"""
import argparse
import json
import struct
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

EPOCH = datetime(1601, 1, 1)
VERSIONS = {0x11: "XP/2003", 0x17: "Vista/Win7", 0x1A: "Win8/8.1",
            0x1E: "Win10", 0x1F: "Win11"}
# Per libscca: v17 keeps one FILETIME at 0x78 and the count at 0x90;
# v23 keeps one at 0x80 and the count at 0x98; v26+ keeps eight slots
# from 0x80 with the count at 0xD0 - or 0xC8 on the v30-variant-2 /
# v31 layout, told apart by the file-metrics-array offset at 0x54
# (0x130 -> 0xD0, 0x128 -> 0xC8).
RUN_COUNT = {0x11: 0x90, 0x17: 0x98, 0x1A: 0xD0, 0x1E: 0xD0,
             0x1F: 0xC8}


def _count_offset(data, ver):
    if ver in (0x1E, 0x1F):
        marker = struct.unpack("<I", data[0x54:0x58])[0]
        return 0xC8 if marker == 0x128 else 0xD0
    return RUN_COUNT.get(ver)


def _ft(b):
    v = struct.unpack("<Q", b[:8])[0]
    if not v:
        return None
    try:
        return (EPOCH + timedelta(microseconds=v / 10)).isoformat()
    except OverflowError:
        return None


def parse_pf(path):
    data = Path(path).read_bytes()
    if data[:4] == b"MAM\x04":
        return {"error": "MAM-compressed prefetch body - needs "
                         "libscca/PECmd on this file", "mam": True}
    if len(data) < 0x98 or data[4:8] != b"SCCA":
        return {"error": "not a prefetch file (no SCCA signature)"}
    ver = struct.unpack("<I", data[:4])[0]
    out = {"version": {"value": hex(ver),
                       "name": VERSIONS.get(ver, "unknown")},
           "executable": data[16:16 + 120].decode("utf-16-le",
                                                  "replace")
           .split("\x00")[0]}
    rco = _count_offset(data, ver)
    if rco and len(data) >= rco + 4:
        out["run_count"] = struct.unpack("<I", data[rco:rco + 4])[0]
    if ver >= 0x1A:
        out["last_run_times"] = [
            t for i in range(8)
            if (t := _ft(data[0x80 + i * 8:0x88 + i * 8]))]
    elif ver == 0x17:
        out["last_run_times"] = [
            t for t in [_ft(data[0x80:0x88])] if t]
    else:
        out["last_run_times"] = [
            t for t in [_ft(data[0x78:0x80])] if t]
    return out


def _selftest():
    pf = bytearray(0xE0)
    struct.pack_into("<I", pf, 0, 0x17)          # v23: 1 slot @0x80
    pf[4:8] = b"SCCA"
    name = "FLAG.EXE".encode("utf-16-le")
    pf[16:16 + len(name)] = name
    struct.pack_into("<Q", pf, 0x80, 133000000000000000)
    struct.pack_into("<I", pf, 0x98, 7)
    tmp = Path(tempfile.mkdtemp()) / "FLAG.EXE-1234ABCD.pf"
    tmp.write_bytes(bytes(pf))
    out = parse_pf(tmp)
    assert out["executable"] == "FLAG.EXE", out
    assert out["run_count"] == 7, out
    assert len(out["last_run_times"]) == 1, out
    # Win8 shape: eight slots at 0x80, count at 0xD0
    pf8 = bytearray(0xE0)
    struct.pack_into("<I", pf8, 0, 0x1A)
    pf8[4:8] = b"SCCA"
    pf8[16:16 + len(name)] = name
    struct.pack_into("<I", pf8, 0xD0, 3)
    for i in range(2):
        struct.pack_into("<Q", pf8, 0x80 + i * 8,
                         133000000000000000 + i * 1000000)
    tmp.write_bytes(bytes(pf8))
    out8 = parse_pf(tmp)
    assert out8["run_count"] == 3 and len(out8["last_run_times"]) == 2, out8
    print("prefetch selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="read an uncompressed .pf prefetch file")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    print(json.dumps(parse_pf(a.file), indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
