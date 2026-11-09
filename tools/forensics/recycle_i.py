#!/usr/bin/env python3
"""recycle_i.py -- decode $Recycle.Bin $I* metadata files.

Usage:
  python3 tools/forensics/recycle_i.py '$I0ABC12.bin'
  python3 tools/forensics/recycle_i.py --selftest

Format: version(8), original file size(8), deletion FILETIME(8), then
the original full path - a fixed 520-byte UTF-16 field on version 1
(Vista/7), a u32 length + UTF-16 string on version 2 (8+). The
deletion timestamp inside $I is the evidence $MFT cannot give: MFT
records are reused, $I files are not.
"""
import argparse
import json
import struct
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

EPOCH = datetime(1601, 1, 1)


def _ft(b):
    v = struct.unpack("<Q", b[:8])[0]
    if not v:
        return None
    try:
        return (EPOCH + timedelta(microseconds=v / 10)).isoformat()
    except OverflowError:
        return None


def parse_i(path):
    data = Path(path).read_bytes()
    if len(data) < 24:
        return {"error": "too small for a $I file"}
    version = struct.unpack("<Q", data[:8])[0]
    size = struct.unpack("<Q", data[8:16])[0]
    when = _ft(data[16:24])
    if version == 1:
        path_s = data[24:544].decode("utf-16-le", "replace") \
            .split("\x00")[0]
    else:
        n = struct.unpack("<I", data[24:28])[0]
        path_s = data[28:28 + n * 2].decode("utf-16-le", "replace")
    return {"version": version, "original_size": size,
            "deleted_at": when, "original_path": path_s}


def _selftest():
    p = "C:\\Users\\victim\\flag.txt".encode("utf-16-le")
    body = struct.pack("<QQQ", 2, 4096, 133000000000000000) + \
        struct.pack("<I", len(p) // 2) + p
    tmp = Path(tempfile.mkdtemp()) / "IXYZ"
    tmp.write_bytes(body)
    out = parse_i(tmp)
    assert out["original_path"] == "C:\\Users\\victim\\flag.txt", out
    assert out["deleted_at"].startswith("2022-06-18"), out
    print("recycle_i selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="decode $Recycle.Bin $I metadata")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    print(json.dumps(parse_i(a.file), indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
