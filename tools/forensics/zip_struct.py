#!/usr/bin/env python3
"""zip_struct.py -- walk a zip's LOCAL headers + diff vs central dir.

zipfile reads only the central directory; a file written into the
archive but never registered there (or removed after) is invisible
to unzip -l yet its bytes sit right there in a LOCAL header — a
standard hide. This walks every PK\\x03\\x04 local header in order,
collects PK\\x01\\x02 central entries, and diffs the two sets.

  python3 tools/forensics/zip_struct.py a.zip list
  python3 tools/forensics/zip_struct.py a.zip get NAME     # local walk
  python3 tools/forensics/zip_struct.py --selftest

`get` extracts by local header (data-descriptor zips report the
declared-in-CD size only — flagged). Bit 3 of flags means size lives
in the post-data descriptor; handled via the CD entry if one exists.
"""
import argparse
import json
import struct
import sys
import zlib


def locals_(data):
    out, off = [], 0
    while True:
        i = data.find(b"PK\x03\x04", off)
        if i < 0:
            break
        if i + 30 > len(data):
            break
        (ver, fl, method, _t, _d, crc, csize, usize,
         nl, el) = struct.unpack("<HHHHHIIIHH", data[i + 4:i + 30])
        name = data[i + 30:i + 30 + nl].decode("utf-8", "replace")
        out.append({"name": name, "offset": i, "flags": fl,
                    "method": method, "crc": hex(crc),
                    "csize": csize, "usize": usize,
                    "data_off": i + 30 + nl + el,
                    "descriptor": bool(fl & 8)})
        off = i + 4
    return out


def centrals(data):
    out, off = [], 0
    while True:
        i = data.find(b"PK\x01\x02", off)
        if i < 0 or i + 46 > len(data):
            break
        (ver, _vb, fl, method, _t, _d, crc, csize, usize,
         nl, el, cl, _disk, _ia, _ea, lho) = struct.unpack(
            "<HHHHHHIIIHHHHHII", data[i + 4:i + 46])
        name = data[i + 46:i + 46 + nl].decode("utf-8", "replace")
        out.append({"name": name, "method": method, "crc": hex(crc),
                    "csize": csize, "usize": usize,
                    "local_off": lho})
        off = i + 4
    return out


def extract(data, name):
    loc = next((e for e in locals_(data) if e["name"] == name), None)
    if not loc:
        return None
    size = loc["csize"]
    if loc["descriptor"] and size == 0:
        cd = next((c for c in centrals(data) if c["name"] == name),
                  None)
        size = cd["csize"] if cd else None
    if size is None:
        return None
    raw = data[loc["data_off"]:loc["data_off"] + size]
    if loc["method"] == 8:
        return zlib.decompress(raw, -15)
    return raw


def report(data):
    loc, cd = locals_(data), centrals(data)
    ln, cn = {e["name"] for e in loc}, {c["name"] for c in cd}
    return {"local_entries": loc, "central_entries": cd,
            "local_only": sorted(ln - cn),
            "central_only": sorted(cn - ln),
            "note": "local_only names = files present but unregistered"
                    " — classic hidden-entry hide"}


def _selftest():
    def local(name, body):
        nb = name.encode()
        return (b"PK\x03\x04" +
                struct.pack("<HHHHHIIIHH", 20, 0, 0, 0, 0,
                            zlib.crc32(body), len(body), len(body),
                            len(nb), 0) + nb + body)
    def cent(name, body, lho):
        nb = name.encode()
        return (b"PK\x01\x02" +
                struct.pack("<HHHHHHIIIHHHHHII", 20, 20, 0, 0, 0, 0,
                            zlib.crc32(body), len(body), len(body),
                            len(nb), 0, 0, 0, 0, 0, lho) + nb)
    vis = local("visible.txt", b"seen")
    hid_off = len(vis)
    hid = local("hidden.txt", b"flag{in_local_only}")
    cd = cent("visible.txt", b"seen", 0)
    z = vis + hid + cd + b"PK\x05\x06" + b"\x00" * 18
    r = report(z)
    assert r["local_only"] == ["hidden.txt"], r
    assert extract(z, "hidden.txt") == b"flag{in_local_only}"
    print("zip_struct selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="local-header walk + central-dir diff")
    ap.add_argument("path", nargs="?")
    ap.add_argument("cmd", nargs="?", choices=["list", "get"])
    ap.add_argument("name", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.path and a.cmd):
        ap.error("path and cmd required")
    data = open(a.path, "rb").read()
    if a.cmd == "list":
        print(json.dumps(report(data), indent=1))
        return
    if not a.name:
        ap.error("get needs a name")
    out = extract(data, a.name)
    if out is None:
        sys.exit(f"{a.name}: no local entry or unsized descriptor")
    sys.stdout.buffer.write(out)


if __name__ == "__main__":
    raise SystemExit(main())
