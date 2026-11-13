#!/usr/bin/env python3
"""recycle_i.py -- Windows $Recycle.Bin $I* metadata reader.

Every file in a modern `$Recycle.Bin` has an `$I...` metadata twin:
version 1 (Vista-era: header + original size + deletion FILETIME +
fixed 260-char UTF-16 path) or version 2 (Win10: 64-bit path length +
variable path). The matching `$R...` file carries the content itself.
This decodes the $I record to original path, size, and deletion time —
"what was deleted, from where, when" without rifiuti. `--dir` walks a
$Recycle.Bin tree and pairs each $I with its $R (exists/missing).

  python3 tools/forensics/recycle_i.py '$IABC123.txt'
  python3 tools/forensics/recycle_i.py --dir '$Recycle.Bin/S-1-5-21-x'
  python3 tools/forensics/recycle_i.py --selftest
"""
import argparse
import datetime
import json
import os
import struct


def _ft(v):
    try:
        return (datetime.datetime(1601, 1, 1) + datetime.timedelta(
            microseconds=v / 10)).isoformat()
    except (OverflowError, OSError, ValueError):
        return "0x%x" % v


def parse(data):
    if len(data) < 8:
        return {"error": "too small for $I header"}
    ver, = struct.unpack("<Q", data[:8])
    if ver == 1:
        if len(data) < 8 + 8 + 8 + 520:
            return {"error": "truncated v1 record", "version": 1}
        size, ts = struct.unpack("<QQ", data[8:24])
        path = data[24:24 + 520].decode(
            "utf-16-le", "replace").rstrip("\x00")
        return {"version": 1, "size": size, "deleted": _ft(ts),
                "original_path": path}
    if ver == 2:
        if len(data) < 28:
            return {"error": "truncated v2 record", "version": 2}
        size, ts, nlen = struct.unpack("<QQI", data[8:28])
        path = data[28:28 + nlen * 2].decode(
            "utf-16-le", "replace").rstrip("\x00")
        return {"version": 2, "size": size, "deleted": _ft(ts),
                "original_path": path}
    return {"error": "unknown $I version %d" % ver, "version": ver}


def _selftest():
    # v2 record
    name = "C:\\Users\\x\\flag.txt".encode("utf-16-le")
    rec = struct.pack("<QQQI", 2, 1337, 133485000000000000,
                      len(name) // 2 + 1) + name + b"\x00\x00"
    out = parse(rec)
    assert out["version"] == 2
    assert out["original_path"] == "C:\\Users\\x\\flag.txt"
    assert out["size"] == 1337
    # v1 record
    p = "D:\\secret\\old.zip".encode("utf-16-le")
    rec = struct.pack("<QQQ", 1, 55, 133485000000000000) \
        + p + b"\x00" * (520 - len(p))
    out = parse(rec)
    assert out["version"] == 1
    assert out["original_path"] == "D:\\secret\\old.zip"
    # pair check on a temp dir
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        open(os.path.join(d, "$IAAA.txt"), "wb").write(rec)
        open(os.path.join(d, "$RAAA.txt"), "wb").write(b"data")
        open(os.path.join(d, "$IBBB.txt"), "wb").write(rec)
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            _dir(d)
        listing = json.loads(buf.getvalue())
        by = {e["i_file"]: e for e in listing["entries"]}
        assert by["$IAAA.txt"]["r_exists"] is True
        assert by["$IBBB.txt"]["r_exists"] is False
    print("recycle_i selftest: ok")


def _dir(d):
    entries = []
    for fn in sorted(os.listdir(d)):
        if not fn.startswith("$I"):
            continue
        p = os.path.join(d, fn)
        if not os.path.isfile(p):
            continue
        rec = parse(open(p, "rb").read())
        rec["i_file"] = fn
        rf = os.path.join(d, "$R" + fn[2:])
        rec["r_exists"] = os.path.exists(rf)
        entries.append(rec)
    print(json.dumps({"entries": entries, "count": len(entries)},
                     indent=1))


def main():
    ap = argparse.ArgumentParser(description="$Recycle.Bin $I reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--dir", metavar="DIR")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.dir:
        return _dir(a.dir)
    if not a.path:
        ap.error("path or --dir required")
    print(json.dumps(parse(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
