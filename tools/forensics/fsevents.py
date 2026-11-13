#!/usr/bin/env python3
"""fsevents.py -- macOS .fseventsd/*.gz event log reader.

macOS forensic bundles ship `/.fseventsd/00000000000*` files: gzipped
pages beginning '1SLD' or '2SLD', each followed by event records --
an event id, flag bits, and a NUL-terminated UTF-8 path (v2 adds a
64-bit id). This answers "what was created/deleted/renamed, and in
which directory" on a macOS image without `fsevents-parser`. Flags
are decoded to the common set (Created/Removed/Renamed/Modified/
Folder/File/HardLink/SymLink); a raw-flags field keeps the exact
bits for anything unusual.

  python3 tools/forensics/fsevents.py events.gz
  python3 tools/forensics/fsevents.py dir/ --all
  python3 tools/forensics/fsevents.py --selftest
"""
import argparse
import gzip
import json
import struct
import sys

FLAGS = {0x00000001: "FolderEvent", 0x00000002: "Mount",
         0x00000004: "Unmount", 0x00000020: "EndOfTransaction",
         0x00000800: "LastHardLinkRemoved", 0x00001000: "HardLink",
         0x00004000: "SymLink", 0x00008000: "FileEvent",
         0x00040000: "PermissionChanged", 0x00080000: "Modified",
         0x00100000: "FinderInfoModified", 0x00200000: "Created",
         0x00400000: "Removed", 0x00800000: "InodeMetaMod",
         0x01000000: "Renamed", 0x02000000: "ModifiedData",
         0x04000000: "ModifiedExtendedAttributes",
         0x08000000: "OwnerChanged", 0x40000000: "Cloned"}


def _decode_flags(v):
    names = [n for b, n in FLAGS.items() if v & b]
    return names


def events(data):
    """yield {id, flags, flag_names, path} per record per page."""
    if data[:2] == b"\x1f\x8b":
        data = gzip.decompress(data)
    out = []
    pos = 0
    while pos + 12 <= len(data):
        p = data.find(b"SLD", pos)
        if p < 1:
            break
        ver = data[p - 1:p]
        if ver not in (b"1", b"2"):
            pos = p + 3
            continue
        e = p + 3 + 4                          # skip page size field
        end = len(data)
        nul = e
        while e < end:
            if ver == b"1":
                if e + 8 > end:
                    break
                eid, flags = struct.unpack("<II", data[e:e + 8])
                e += 8
            else:
                if e + 12 > end:
                    break
                eid, flags = struct.unpack("<QI", data[e:e + 12])
                e += 12
            nul = data.find(b"\x00", e)
            if nul < 0 or nul > e + 4096:
                break
            path = data[e:nul].decode("utf-8", "replace")
            e = nul + 1
            # next page marker?
            if not path or not path.startswith("/"):
                continue
            out.append({"id": eid, "flags": hex(flags),
                        "flag_names": _decode_flags(flags),
                        "path": path})
        pos = nul + 1
    return out


def _selftest():
    recs = b""
    for i, (fl, path) in enumerate((
            (0x00200000 | 0x00008000, "/Users/x/flag.txt"),
            (0x00400000, "/Users/x/old_dir"),
            (0x01000000 | 0x00008000, "/Users/x/renamed.png"))):
        recs += struct.pack("<QI", 0x1000 + i, fl) + path.encode() \
            + b"\x00"
    page = b"2SLD" + b"\x00" * 4 + recs
    blob = gzip.compress(page)
    out = events(blob)
    assert len(out) == 3, out
    assert out[0]["path"] == "/Users/x/flag.txt"
    assert "Created" in out[0]["flag_names"]
    assert "Removed" in out[1]["flag_names"]
    assert "Renamed" in out[2]["flag_names"]
    print("fsevents selftest: ok")


def main():
    ap = argparse.ArgumentParser(description=".fseventsd reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    import os
    evs = []
    if os.path.isdir(a.path):
        for fn in sorted(os.listdir(a.path)):
            p = os.path.join(a.path, fn)
            if os.path.isfile(p):
                try:
                    evs += events(open(p, "rb").read())
                except Exception:
                    pass
        evs.sort(key=lambda e: e["id"])
    else:
        evs = events(open(a.path, "rb").read())
    print(json.dumps({"events": evs, "count": len(evs)}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
