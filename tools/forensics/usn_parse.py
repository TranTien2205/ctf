#!/usr/bin/env python3
"""usn_parse.py -- parse $UsnJrnl:$J records to JSONL.

Usage:
  python3 tools/forensics/usn_parse.py UsnJrnl.bin
  python3 tools/forensics/usn_parse.py UsnJrnl.bin --deleted
  python3 tools/forensics/usn_parse.py --selftest

Each record: reclen(4) major(2) minor(2) fileref(8) parentref(8)
usn(8) timestamp FILETIME(8) reason(4) srcinfo(4) secid(4)
fileattrs(4) namelen(2) nameoff(2) utf16 name. $J is the ordering
source an $MFT cannot give: records are appended, never rewritten, so
the sequence itself is the timeline. Reason bits are decoded against
the documented names.
"""
import argparse
import json
import struct
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

EPOCH = datetime(1601, 1, 1)
REASONS = {
    0x00000001: "DATA_OVERWRITE", 0x00000002: "DATA_EXTEND",
    0x00000004: "DATA_TRUNCATION", 0x00000010: "NAMED_DATA_OVERWRITE",
    0x00000020: "NAMED_DATA_EXTEND", 0x00000040: "NAMED_DATA_TRUNCATION",
    0x00000100: "FILE_CREATE", 0x00000200: "FILE_DELETE",
    0x00000400: "EA_CHANGE", 0x00000800: "SECURITY_CHANGE",
    0x00001000: "RENAME_OLD_NAME", 0x00002000: "RENAME_NEW_NAME",
    0x00004000: "INDEXABLE_CHANGE", 0x00008000: "BASIC_INFO_CHANGE",
    0x00010000: "HARD_LINK_CHANGE", 0x00020000: "COMPRESSION_CHANGE",
    0x00040000: "ENCRYPTION_CHANGE", 0x00080000: "OBJECT_ID_CHANGE",
    0x00100000: "REPARSE_POINT_CHANGE", 0x00200000: "STREAM_CHANGE",
    0x80000000: "CLOSE",
}


def _ft(b):
    v = struct.unpack("<Q", b[:8])[0]
    if not v:
        return None
    try:
        return (EPOCH + timedelta(microseconds=v / 10)).isoformat()
    except OverflowError:
        return None


def parse_j(path):
    data = Path(path).read_bytes()
    rows, off = [], 0
    while off + 60 <= len(data):
        if data[off:off + 8] == b"\x00" * 8:
            off += 8
            continue
        reclen = struct.unpack("<I", data[off:off + 4])[0]
        if reclen < 60 or off + reclen > len(data):
            break
        rec = data[off:off + reclen]
        nlen, noff = struct.unpack("<HH", rec[56:60])
        name = rec[noff:noff + nlen].decode("utf-16-le", "replace")
        reason = struct.unpack("<I", rec[40:44])[0]
        rows.append({
            "usn": struct.unpack("<Q", rec[24:32])[0],
            "file_ref": struct.unpack("<Q", rec[8:16])[0] & 0xFFFFFFFFFFFF,
            "parent_ref": struct.unpack("<Q", rec[16:24])[0]
            & 0xFFFFFFFFFFFF,
            "time": _ft(rec[32:40]),
            "reason": {"value": hex(reason),
                       "names": [n for b, n in REASONS.items()
                                 if reason & b]},
            "name": name})
        off += (reclen + 7) & ~7
    return rows


def _selftest():
    def rec(usn, reason, name):
        n = name.encode("utf-16-le")
        r = bytearray(60 + len(n))
        struct.pack_into("<IHH", r, 0, len(r), 2, 0)
        struct.pack_into("<QQQQ", r, 8, 42, 5, usn,
                         133000000000000000)
        struct.pack_into("<IIII", r, 40, reason, 0, 0, 0x20)
        struct.pack_into("<HH", r, 56, len(n), 60)
        r[60:] = n
        r += b"\x00" * ((8 - len(r) % 8) % 8)   # records are 8-aligned
        return bytes(r)
    tmp = Path(tempfile.mkdtemp()) / "J"
    tmp.write_bytes(rec(100, 0x100, "flag.txt") +
                    b"\x00" * 16 +
                    rec(101, 0x200 | 0x80000000, "flag.txt"))
    rows = parse_j(tmp)
    assert len(rows) == 2, rows
    assert rows[0]["name"] == "flag.txt"
    assert "FILE_CREATE" in rows[0]["reason"]["names"]
    assert "FILE_DELETE" in rows[1]["reason"]["names"]
    print("usn_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="parse $UsnJrnl:$J records to JSONL")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--deleted", action="store_true",
                    help="only FILE_DELETE/RENAME_OLD_NAME reasons")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    for r in parse_j(a.file):
        if a.deleted and not (
                {"FILE_DELETE", "RENAME_OLD_NAME"}
                & set(r["reason"]["names"])):
            continue
        print(json.dumps(r))


if __name__ == "__main__":
    raise SystemExit(main())
