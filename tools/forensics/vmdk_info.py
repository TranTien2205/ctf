#!/usr/bin/env python3
"""vmdk_info.py -- VMDK descriptor and sparse-extent inventory.

A `.vmdk` in a forensic bundle is either a small TEXT descriptor
('# Disk DescriptorFile', extent lines 'RW <secs> <type> "<file>"'),
or a self-contained sparse binary (magic 'KDMV' with grain tables).
This tool parses the descriptor form fully: CID, create-type, every
extent's sectors/type/file, cylinders/heads/sectors geometry, and
the parent-filename chain for snapshot links -- everything needed
to open the flat extent with part_table/fat_read directly. A sparse
'KDMV' extent is identified with its header fields (capacity, grain
size, directory pointer) and named for grain-table work rather than
guessed.

  python3 tools/forensics/vmdk_info.py disk.vmdk
  python3 tools/forensics/vmdk_info.py --selftest
"""
import argparse
import json
import re
import struct
import sys


def _descriptor(txt):
    out = {"format": "vmdk-descriptor", "extents": []}
    cid = re.search(r"CID=([0-9a-fA-F]+)", txt)
    if cid:
        out["cid"] = cid.group(1)
    ct = re.search(r'createType="([^"]+)"', txt)
    if ct:
        out["create_type"] = ct.group(1)
    for m in re.finditer(r'^([A-Z]+)\s+(\d+)\s+([A-Z]+)\s+"([^"]+)"',
                         txt, re.M):
        acc, secs, typ, fn = m.groups()
        out["extents"].append({"access": acc, "sectors": int(secs),
                               "type": typ, "file": fn})
    for k in ("cylinders", "heads", "sectors"):
        g = re.search(
            r'(?:ddb|dsk)\.geometry\.%s\s*=\s*"?(\d+)' % k, txt)
        if g:
            out[k] = int(g.group(1))
    par = re.search(r'parentFileNameHint="([^"]+)"', txt)
    if par:
        out["parent_hint"] = par.group(1)
    pcid = re.search(r"parentCID=([0-9a-fA-F]+)", txt)
    if pcid:
        out["parent_cid"] = pcid.group(1)
    out["total_sectors"] = sum(e["sectors"] for e in out["extents"]
                               if e["type"] not in ("ZERO",))
    return out


def _sparse(data):
    if data[:4] != b"KDMV":
        return None
    out = {"format": "vmdk-sparse (KDMV)"}
    ver, flags, cap, gsz, gtdir_off = struct.unpack(
        "<IIQQQ", data[4:36])
    out.update({"version": ver, "flags": hex(flags),
                "capacity_sectors": cap, "grain_size_sectors": gsz,
                "grain_dir_offset": gtdir_off,
                "note": "sparse extent -- grain table at the dir "
                        "offset; open the descriptor's extents "
                        "individually"})
    return out


def parse(data):
    if data[:4] == b"KDMV":
        return _sparse(data)
    try:
        txt = data.decode("utf-8", "replace")
    except Exception:
        return {"error": "unrecognised vmdk container"}
    if "# Disk DescriptorFile" in txt or "createType=" in txt:
        return _descriptor(txt)
    return {"error": "not a vmdk descriptor or KDMV sparse"}


def _selftest():
    txt = ("# Disk DescriptorFile\n"
           "version=1\n"
           "CID=deadbeef\n"
           "parentCID=ffffffff\n"
           'createType="monolithicSparse"\n'
           "\n"
           "# Extent description\n"
           'RW 4096 SPARSE "disk-s001.vmdk"\n'
           'RW 4096 FLAT "disk-flat.vmdk" 0\n'
           "\n"
           "# The Disk Data Base\n"
           "#DDB\n"
           "ddb.virtualHWVersion = \"4\"\n"
           "ddb.geometry.cylinders = \"4\"\n"
           "ddb.geometry.heads = \"255\"\n"
           "ddb.geometry.sectors = \"63\"\n"
           'ddb.adapterType = "ide"\n'
           'ddb.toolsInstallType = "4"\n'
           "ddb.uuid = \"60 00 C2 9f 4f 24 35 33-8c 44 d4 40 27 6f flag\"\n"
           'parentFileNameHint="base.vmdk"\n')
    r = parse(txt.encode())
    assert r["cid"] == "deadbeef" and r["parent_cid"] == "ffffffff"
    assert len(r["extents"]) == 2 and r["extents"][1]["type"] == "FLAT"
    assert r["total_sectors"] == 8192, r
    assert r["sectors"] == 63 and r["heads"] == 255
    assert r["parent_hint"] == "base.vmdk"
    sp = b"KDMV" + struct.pack("<IIQQQ", 3, 0x30001, 8192, 128, 1234)
    r2 = parse(sp.ljust(512, b"\x00"))
    assert r2["capacity_sectors"] == 8192 and \
        r2["grain_size_sectors"] == 128, r2
    print("vmdk_info selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="VMDK inventory")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    print(json.dumps(parse(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
