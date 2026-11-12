#!/usr/bin/env python3
"""cab_list.py -- Microsoft CABINET archive listing and extraction.

`.cab` (and `.msu`/driver packages) still show up in Windows DFIR
bundles; `cabextract`/`expand` are not assumed. The container is a
CFHEADER, CFFOLDER table, CFFILE name list, and CFDATA blocks. This
tool lists members honestly, and extracts what it can: uncompressed
folders and MSZIP folders (each CFDATA block is 'CK' + a raw deflate
stream -- inflate per block). LZX/LZX-encrypted folders are named
with their compression type and left alone rather than guessed.

  python3 tools/forensics/cab_list.py pack.cab
  python3 tools/forensics/cab_list.py pack.cab --extract NAME --to DIR
  python3 tools/forensics/cab_list.py --selftest
"""
import argparse
import json
import struct
import sys
import zlib

COMP = {0: "none", 1: "MSZIP", 2: "Quantum", 3: "LZX"}


def parse(data):
    if len(data) < 36 or data[:4] != b"MSCF":
        return {"error": "not a cabinet (bad magic)"}
    cb_cab, _r2, files_off, _r3 = struct.unpack("<IIII", data[8:24])
    _vmin, _vmaj, nfolders, nfiles, flags, _setid, _icab = \
        struct.unpack("<2B5H", data[24:36])
    pos = 36
    if flags & 0x4:                                  # prev/next cabinet
        pos += 20
    folders = []
    for _ in range(nfolders):
        coff, cdata, comp = struct.unpack("<IIH", data[pos:pos + 10])
        folders.append({"data_off": coff, "blocks": cdata,
                        "compression": COMP.get(comp & 0xF,
                                                "0x%x" % comp)})
        pos += 10
    files = []
    pos = files_off
    for _ in range(nfiles):
        size, uoff, ifold = struct.unpack("<IIH", data[pos:pos + 10])
        name_end = data.index(b"\x00", pos + 10)
        name = data[pos + 10:name_end].decode("utf-8", "replace")
        files.append({"name": name, "size": size, "offset": uoff,
                      "folder": ifold})
        pos = name_end + 1
    return {"size": cb_cab, "folders": folders, "files": files,
            "extractable": sorted({f["compression"] for f in folders
                                   if f["compression"] in
                                   ("none", "MSZIP")})}


def extract(data, name):
    meta = parse(data)
    for f in meta["files"]:
        if f["name"] != name:
            continue
        folder = meta["folders"][f["folder"]]
        if folder["compression"] not in ("none", "MSZIP"):
            return {"error": "folder uses %s compression -- "
                    "named, not extracted" % folder["compression"]}
        out = bytearray()
        p = folder["data_off"]
        for _ in range(folder["blocks"]):
            _ck, cb, ucb = struct.unpack("<IHH", data[p:p + 8])
            blk = data[p + 8:p + 8 + cb]
            if folder["compression"] == "MSZIP":
                if blk[:2] != b"CK":
                    return {"error": "bad MSZIP block marker"}
                out += zlib.decompress(blk[2:], -15)
            else:
                out += blk[:ucb]
            p += 8 + cb
        body = bytes(out[f["offset"]:f["offset"] + f["size"]])
        return {"name": name, "data": body, "size": len(body)}
    return {"error": "member not found"}


def _selftest():
    body = b"flag{in_a_cab}" + b"\x00" * 3
    name = b"flag.txt\x00"
    # layout: CFHEADER(36) | CFFOLDER | CFFILE(s) | CFDATA
    files_off = 36 + 10
    cffile = struct.pack("<IIH", len(body), 0, 0) + name
    data_off = files_off + len(cffile)
    total = data_off + 8 + len(body)
    hdr = (b"MSCF" + struct.pack("<I", 0)
           + struct.pack("<I", total)
           + struct.pack("<I", 0)
           + struct.pack("<I", files_off)
           + struct.pack("<I", 0)
           + struct.pack("<2B5H", 3, 1, 1, 1, 0, 0, 0))
    cfold = struct.pack("<IIH", data_off, 1, 0)
    cfdata = struct.pack("<IHH", 0, len(body), len(body)) + body
    blob = hdr + cfold + cffile + cfdata
    m = parse(blob)
    assert m["files"][0]["name"] == "flag.txt", m
    r = extract(blob, "flag.txt")
    assert r["data"].rstrip(b"\x00") == b"flag{in_a_cab}", r
    # MSZIP block: 'CK' + raw deflate
    comp = zlib.compress(body)[2:-4]                   # raw deflate
    blk = b"CK" + comp
    cfold_z = struct.pack("<IIH", data_off, 1, 1)
    cfdata_z = struct.pack("<IHH", 0, len(blk), len(body)) + blk
    blob2 = hdr + cfold_z + cffile + cfdata_z
    r2 = extract(blob2, "flag.txt")
    assert r2["data"].rstrip(b"\x00") == b"flag{in_a_cab}", r2
    print("cab_list selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="CABINET archive reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--extract", metavar="NAME")
    ap.add_argument("--to", default=".")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    if a.extract:
        r = extract(data, a.extract)
        if "data" in r:
            dest = "%s/%s" % (a.to, a.extract.replace("/", "_"))
            open(dest, "wb").write(r["data"])
            r = {"wrote": dest, "size": r["size"]}
        print(json.dumps(r))
        return
    print(json.dumps(parse(data), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
