#!/usr/bin/env python3
"""dmg_udif.py -- Apple UDIF .dmg inventory + decompressed extract.

macOS forensic bundles ship `.dmg` images and `dmg2img`/`hdiutil`
are absent. UDIF layout: a 512-byte `koly` trailer at EOF carries
xmlOffset/xmlLength pointing at a plist whose `blkx` entries each
embed a `mish` block table. Every table row maps
(out-sector-number, out-sector-count, in-file-offset, in-length,
codec): type 0 = zero-fill, 1 = verbatim copy, 0x80000004 = zlib,
0x80000005 = bzip2, others named and skipped. This walks every
mish table and either lists the layout or writes a flat image that
part_table / fat_read / ext_read / hive_parse can consume.

  python3 tools/forensics/dmg_udif.py a.dmg
  python3 tools/forensics/dmg_udif.py a.dmg --extract flat.img
  python3 tools/forensics/dmg_udif.py --selftest
"""
import argparse
import base64
import bz2
import json
import plistlib
import struct
import zlib

BLK_TYPE = {0x00000000: "zerofill", 0x00000001: "raw",
            0x00000002: "ignore", 0x80000004: "zlib",
            0x80000005: "bzip2", 0x80000006: "lzfse",
            0x7ffffffe: "comment", 0xffffffff: "end"}


def _koly(d):
    if len(d) < 512:
        return None
    t = d[-512:]
    if t[:4] != b"koly":
        return None
    return {"version": struct.unpack(">I", t[4:8])[0],
            "data_fork_offset": struct.unpack(">Q", t[24:32])[0],
            "data_fork_length": struct.unpack(">Q", t[32:40])[0],
            "xml_offset": struct.unpack(">Q", t[216:224])[0],
            "xml_length": struct.unpack(">Q", t[224:232])[0],
            "sector_count": struct.unpack(">Q", t[492:500])[0]}


def _mish(blob):
    if len(blob) < 40 or blob[:4] != b"mish":
        return []
    nsec, = struct.unpack(">Q", blob[8:16])
    ssec, = struct.unpack(">Q", blob[16:24])
    nblk, = struct.unpack(">I", blob[36:40])
    rows = []
    p = 40
    for _ in range(nblk):
        if p + 40 > len(blob):
            break
        typ, _c = struct.unpack(">II", blob[p:p + 8])
        ossec, ocnt, ioff, ilen = struct.unpack(
            ">QQQQ", blob[p + 8:p + 40])
        rows.append({"type": BLK_TYPE.get(typ, "0x%x" % typ),
                     "out_sector": ossec, "out_count": ocnt,
                     "in_offset": ioff, "in_length": ilen})
        p += 40
        if typ == 0xFFFFFFFF:
            break
    return rows


def parse(path):
    d = open(path, "rb").read()
    k = _koly(d)
    if not k:
        return {"error": "no koly trailer (not a UDIF dmg)"}
    out = dict(k)
    xml = d[k["xml_offset"]:k["xml_offset"] + k["xml_length"]]
    try:
        pl = plistlib.loads(xml)
    except Exception as e:
        out["error"] = "resource plist unreadable: %s" % e
        return out
    blocks = []
    for i, ent in enumerate(pl.get("resource-fork", {}).get(
            "blkx", [])):
        blob = ent.get("Data")
        if isinstance(blob, bytes) and blob[:4] == b"mish":
            for r in _mish(blob):
                r["table"] = i
                blocks.append(r)
    out["block_rows"] = blocks
    out["chunks"] = len(blocks)
    return out, d


def extract(d, out, dst):
    rows = [r for r in out.get("block_rows", [])
            if r["type"] not in ("end", "comment")]
    total = max((r["out_sector"] + r["out_count"]) * 512
                for r in rows) if rows else 0
    with open(dst, "wb") as f:
        f.truncate(total)
        skipped = []
        for r in rows:
            if r["out_count"] == 0:
                continue
            f.seek(r["out_sector"] * 512)
            if r["type"] == "zerofill":
                f.write(b"\x00" * min(r["out_count"] * 512, 1 << 22))
            elif r["type"] == "raw":
                f.write(d[r["in_offset"]:
                          r["in_offset"] + r["in_length"]])
            elif r["type"] in ("zlib", "bzip2"):
                src = d[r["in_offset"]:r["in_offset"] + r["in_length"]]
                try:
                    dec = zlib.decompress(src) if r["type"] == "zlib" \
                        else bz2.decompress(src)
                    f.write(dec[:r["out_count"] * 512])
                except Exception as e:
                    skipped.append({"row": r, "err": str(e)})
            else:
                skipped.append({"row": r, "err": "unsupported codec"})
        return {"written": total, "skipped": skipped}


def _selftest():
    sector = 512
    # three output chunks: raw s0, zlib s1 (flag), zerofill s2
    raw = b"H" * sector
    comp = zlib.compress(b"flag{dmg_udif}" + b"\x00" * (sector - 14))
    mish = bytearray(b"mish" + b"\x00" * 36)
    struct.pack_into(">I", mish, 4, 4)
    struct.pack_into(">I", mish, 36, 4)         # 4 block rows
    rows = [(1, 0, 0, 1, 0, len(raw)),
            (0x80000004, 0, 1, 1, len(raw), len(comp)),
            (0, 0, 2, 1, 0, 0),
            (0xFFFFFFFF, 0, 3, 0, 0, 0)]
    body = bytearray()
    for t, c, os_, oc, io_, il in rows:
        body += struct.pack(">IIQQQQ", t, c, os_, oc, io_, il)
    mish += body
    pl = {"resource-fork": {"blkx": [
        {"Name": "part", "ID": "0", "Data": bytes(mish)}]}}
    xml = plistlib.dumps(pl)
    data_fork = raw + comp
    img = bytearray(data_fork + b"\x00" * 8 + xml)
    xml_off = len(data_fork) + 8
    trailer = bytearray(512)
    trailer[:4] = b"koly"
    struct.pack_into(">I", trailer, 4, 5)
    struct.pack_into(">QQ", trailer, 24, 0, len(data_fork))
    struct.pack_into(">QQ", trailer, 216, xml_off, len(xml))
    struct.pack_into(">Q", trailer, 492, 3)
    img += trailer
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".dmg", delete=False) as t:
        t.write(img); p = t.name
    try:
        out, d = parse(p)
        assert out["chunks"] == 4, out
        assert out["block_rows"][1]["type"] == "zlib"
        with tempfile.NamedTemporaryFile(delete=False) as t2:
            dst = t2.name
        res = extract(d, out, dst)
        flat = open(dst, "rb").read()
        assert flat[:sector] == raw
        assert flat[sector:sector + 14] == b"flag{dmg_udif}"
        assert res["skipped"] == []
        print("dmg_udif selftest: ok")
    finally:
        os.unlink(p)
        os.unlink(dst)


def main():
    ap = argparse.ArgumentParser(description="UDIF .dmg inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--extract", help="write decompressed flat image")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    out, d = parse(a.path)
    if a.extract and "block_rows" in out:
        res = extract(d, out, a.extract)
        out["extract"] = res
    out.pop("block_rows", None) if not a.extract else None
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
