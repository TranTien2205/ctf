#!/usr/bin/env python3
"""info2.py -- Windows XP-era RECYCLED\\INFO2 record reader.

Pre-Vista recycle bins (XP/2003, still present in old disk images and
some Sherlock bundles) keep one `INFO2` file instead of per-file $I
metadata. Records are fixed 0x320 bytes: record index (u32), drive
letter byte, original path (260-byte ASCII field, NUL-padded),
physical size (u32), deletion FILETIME (8), and a second UTF-16
copy of the path starting at 0x118 on v5 records. `Dc`/`DcN` files
alongside carry the content; `--dir` pairs them like recycle_i does.

  python3 tools/forensics/info2.py INFO2
  python3 tools/forensics/info2.py --dir RECYCLED
  python3 tools/forensics/info2.py --selftest
"""
import argparse
import datetime
import json
import os
import struct

REC = 0x320
DRIVE = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _ft(v):
    try:
        return (datetime.datetime(1601, 1, 1) + datetime.timedelta(
            microseconds=v / 10)).isoformat()
    except (OverflowError, OSError, ValueError):
        return "0x%x" % v


def parse(data):
    if len(data) < 0x320:
        return {"error": "too small for INFO2 header"}
    ver, = struct.unpack("<I", data[:4])
    if ver not in (5,):
        return {"error": "unknown INFO2 version %d" % ver,
                "version": ver}
    nrec, = struct.unpack("<I", data[8:12])
    recs = []
    pos = 0x320                      # first record after header
    while pos + REC <= len(data) and len(recs) < max(nrec, 1) * 4:
        r = data[pos:pos + REC]
        idx, = struct.unpack("<I", r[:4])
        drive = r[4]
        path_a = r[8:8 + 260].split(b"\x00")[0].decode(
            "latin-1", "replace")
        size, = struct.unpack("<I", r[268:272])
        ts, = struct.unpack("<Q", r[272:280])
        path_w = r[0x118:0x118 + 520].decode(
            "utf-16-le", "replace").rstrip("\x00")
        if path_a or path_w:
            recs.append({"index": idx,
                         "drive": DRIVE[drive] if drive < 26 else
                         hex(drive),
                         "original_path": path_a or path_w,
                         "path_utf16": path_w or None,
                         "size": size, "deleted": _ft(ts)})
        pos += REC
    return {"version": ver, "declared_records": nrec,
            "records": recs}


def _pair(out, directory):
    """Pair each record with its content file: record index N of a file
    deleted from drive D lives as `Dc<N>.<original extension>` in the
    RECYCLED dir. Marks dc_exists False when only the metadata survived."""
    for rec in out.get("records", []):
        base = os.path.splitext(rec.get("original_path") or "")[1]
        name = "Dc%d%s" % (rec["index"], base)
        cand = os.path.join(directory, name)
        rec["dc_file"] = name
        rec["dc_exists"] = os.path.isfile(cand)
        if rec["dc_exists"]:
            rec["dc_size"] = os.path.getsize(cand)
    return out


def _selftest():
    img = bytearray(0x320 * 3)
    struct.pack_into("<I", img, 0, 5)
    struct.pack_into("<I", img, 8, 2)
    for i, (drv, path, size) in enumerate(
            ((2, "Documents\\flag.txt", 1337),
             (3, "secret\\old.zip", 42))):
        r = 0x320 + i * 0x320
        struct.pack_into("<I", img, r, i)
        img[r + 4] = drv
        img[r + 8:r + 8 + len(path)] = path.encode("latin-1")
        struct.pack_into("<II", img, r + 268, size, 0)
        struct.pack_into("<Q", img, r + 272, 133485000000000000)
        pu = path.encode("utf-16-le")
        img[r + 0x118:r + 0x118 + len(pu)] = pu
    out = parse(bytes(img))
    assert out["version"] == 5
    assert len(out["records"]) == 2, out
    r0 = out["records"][0]
    assert r0["drive"] == "C", r0
    assert r0["original_path"] == "Documents\\flag.txt", r0
    assert r0["path_utf16"] == "Documents\\flag.txt"
    assert r0["size"] == 1337
    assert out["records"][1]["drive"] == "D"
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        open(os.path.join(td, "Dc0.txt"), "wb").write(b"x")
        out = _pair(out, td)
        assert out["records"][0]["dc_exists"] is True
        assert out["records"][0]["dc_size"] == 1
        assert out["records"][1]["dc_exists"] is False
        assert out["records"][1]["dc_file"] == "Dc1.zip"
    print("info2 selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="INFO2 (XP recycle bin)")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--dir", help="RECYCLED dir; pairs Dc<N>.<ext> files")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    out = parse(open(a.path, "rb").read())
    if a.dir:
        out = _pair(out, a.dir)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
