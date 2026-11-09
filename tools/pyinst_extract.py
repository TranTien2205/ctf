#!/usr/bin/env python3
"""pyinst_extract.py -- extract a PyInstaller-frozen exe (stdlib).

Usage:
  python3 tools/pyinst_extract.py program.exe outdir
  python3 tools/pyinst_extract.py program.exe --toc
  python3 tools/pyinst_extract.py --selftest

The PyInstaller archive ends with a 'MEI\x0c' cookie holding the
package length and TOC offset; TOC entries are
[structsize u32][pos u32][compressed u32][uncompressed u32][cmpr u8]
[type u8][name]. 's'-type entries are marshalled code objects
(bytecode, not source); 'z'-type is the PYZ archive of modules.
Entries decompress with zlib. Extracted 's' payloads can go straight
to tools/pyc_dis.py after prepending a pyc header.
"""
import argparse
import json
import marshal
import struct
import sys
import tempfile
import zlib
from pathlib import Path

COOKIE = b"MEI\x0c\x0b\x0a\x0b\x0e"
# cookie = magic(8) + pkg_len(4) + toc_off(4) + toc_len(4) +
# pyvers(4) + pylibname(64) = 88 bytes
COOKIE_LEN = 88


def find_pkg(data):
    """locate the MEI cookie near EOF; return (pkg_start, toc_abs,
    toc_len, entries-bytes)."""
    idx = data.rfind(COOKIE)
    if idx < 0:
        return None
    pkg_len, toc_off, toc_len = struct.unpack(
        "<III", data[idx + 8:idx + 20])
    pkg_start = idx + COOKIE_LEN - pkg_len
    return {"pkg_start": pkg_start,
            "toc_abs": pkg_start + toc_off,
            "toc_len": toc_len,
            "pyver": struct.unpack("<I", data[idx + 20:idx + 24])[0]}


def parse_toc(data, pkg):
    toc = zlib.decompress(
        data[pkg["toc_abs"]:pkg["toc_abs"] + pkg["toc_len"]])
    out, pos = [], 0
    while pos + 18 <= len(toc):
        (sz, off, clen, ulen, cmpr, typ) = struct.unpack(
            "<IIII BB", toc[pos:pos + 18])
        name = toc[pos + 18:pos + sz].split(b"\x00")[0] \
            .decode("utf-8", "replace")
        out.append({"name": name, "type": chr(typ),
                    "off": pkg["pkg_start"] + off,
                    "clen": clen, "ulen": ulen, "cmpr": cmpr})
        pos += sz
    return out


def extract(data, e):
    raw = data[e["off"]:e["off"] + e["clen"]]
    return zlib.decompress(raw) if e["cmpr"] else raw


def _selftest():
    # synthetic archive: payload + compressed toc + MEI cookie
    script = marshal.dumps(compile("x='flag{pyinst}'", "<m>", "exec"))
    e1 = zlib.compress(script)
    e2 = zlib.compress(b"PYZ-module-data")
    toc_raw = b""
    off = 0
    for name, typ, blob in ((b"main\x00", ord("s"), e1),
                            (b"PYZ-00\x00", ord("z"), e2)):
        ent = struct.pack("<IIII BB", 0, off, len(blob), 0, 1, typ)
        nlen = len(name) + (18 - len(name) % 8) % 8 or 18
        # real entries pad name to keep entry 8-aligned; keep simple:
        sz = 18 + len(name)
        ent = struct.pack("<IIII BB", sz, off, len(blob),
                          len(zlib.decompress(blob)), 1, typ) + name
        toc_raw += ent
        off += len(blob)
    toc_c = zlib.compress(toc_raw)
    body = b"\x00" * 64 + e1 + e2
    toc_off = len(body)
    body += toc_c
    pkg_len = len(body) - 64 + COOKIE_LEN
    cookie = COOKIE + struct.pack("<IIII", pkg_len, toc_off - 64,
                                  len(toc_c), 0) + b"python3x.dll" \
        .ljust(64, b"\x00")
    blob_all = body + cookie
    pkg = find_pkg(blob_all)
    assert pkg and pkg["pkg_start"] == 64, pkg
    toc = parse_toc(blob_all, pkg)
    assert [e["name"] for e in toc] == ["main", "PYZ-00"], toc
    s = extract(blob_all, toc[0])
    code = marshal.loads(s)
    assert "flag{pyinst}" in code.co_consts
    print("pyinst_extract selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="extract a PyInstaller-frozen executable")
    ap.add_argument("file", nargs="?")
    ap.add_argument("outdir", nargs="?")
    ap.add_argument("--toc", action="store_true",
                    help="list the table of contents only")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    data = Path(a.file).read_bytes()
    pkg = find_pkg(data)
    if not pkg:
        print(json.dumps({"error": "no MEI cookie - not PyInstaller"
                                   " (or UPX-stripped overlay)"}))
        return 1
    toc = parse_toc(data, pkg)
    if a.toc or not a.outdir:
        print(json.dumps({"python": pkg["pyver"], "entries": toc},
                         indent=1))
        if not a.outdir:
            return
    out = Path(a.outdir)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for e in toc:
        blob = extract(data, e)
        p = out / (e["name"].replace("/", "_").replace("\\", "_")
                   or f"entry{e['off']:x}")
        p.write_bytes(blob)
        written.append({"name": e["name"], "type": e["type"],
                        "file": str(p), "size": len(blob)})
    print(json.dumps({"written": written}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
