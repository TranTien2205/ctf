#!/usr/bin/env python3
"""lnk_parse.py -- decode a Windows .lnk (ShellLink) shortcut to JSON.

Usage:
  python3 tools/forensics/lnk_parse.py FILE.lnk
  python3 tools/forensics/lnk_parse.py --selftest

Reads the ShellLinkHeader (76 bytes): timestamps as FILETIME, target
file size and attributes, LinkFlags. Then the optional structures the
flags declare: LinkTargetIDList (item-id strings), LinkInfo (local
base path, common path suffix, volume serial + label), and the string
data blocks (name/relative/arguments/icon/working dir) - unicode or
ANSI per flag. EnvironmentVariable and KnownFolder data blocks are
reported by offset when present.

The fields a Sherlock question usually wants - target path, the three
target timestamps, drive serial - are all top-level keys.
"""
import argparse
import json
import struct
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

EPOCH = datetime(1601, 1, 1)
FLAG_NAMES = {0x0001: "HasTargetIDList", 0x0002: "HasLinkInfo",
              0x0004: "HasName", 0x0008: "HasRelativePath",
              0x0010: "HasWorkingDir", 0x0020: "HasArguments",
              0x0040: "HasIconLocation", 0x0080: "IsUnicode",
              0x0200: "HasExpString", 0x0400: "RunInSeparateProcess",
              0x0800: "HasDarwinID", 0x1000: "RunAsUser",
              0x2000: "HasExpIcon", 0x4000: "NoPidlAlias",
              0x8000: "RunWithShimLayer", 0x20000: "EnableTargetMetadata"}
STRING_FLAGS = [(0x0004, "name_string"), (0x0008, "relative_path"),
                (0x0010, "working_dir"), (0x0020, "arguments"),
                (0x0040, "icon_location")]
DRIVE_TYPES = {0: "UNKNOWN", 1: "NO_ROOT_DIR", 2: "REMOVABLE",
               3: "FIXED", 4: "REMOTE", 5: "CDROM", 6: "RAMDISK"}


def _ft(b):
    v = struct.unpack("<Q", b[:8])[0]
    if not v:
        return None
    try:
        return (EPOCH + timedelta(microseconds=v / 10)).isoformat()
    except OverflowError:
        return None


def _cstr(b, enc="mbcs"):
    end = b.find(b"\x00")
    if end < 0:
        end = len(b)
    return b[:end].decode(enc, "replace")


def parse_lnk(path):
    data = Path(path).read_bytes()
    if len(data) < 76 or data[:4] != b"\x4c\x00\x00\x00":
        return {"error": "not a ShellLink file"}
    if data[4:20] != bytes.fromhex("0114020000000000c000000000000046"):
        return {"error": "LinkCLSID mismatch"}
    flags = struct.unpack("<I", data[20:24])[0]
    out = {"flags": {"value": hex(flags),
                     "names": [n for b, n in FLAG_NAMES.items()
                              if flags & b]},
           "file_attributes": hex(struct.unpack("<I", data[24:28])[0]),
           "created": _ft(data[28:36]),
           "accessed": _ft(data[36:44]),
           "modified": _ft(data[44:52]),
           "file_size": struct.unpack("<I", data[52:56])[0],
           "icon_index": struct.unpack("<i", data[56:60])[0],
           "show_command": struct.unpack("<I", data[60:64])[0],
           "hotkey": hex(struct.unpack("<H", data[64:66])[0])}
    uni = bool(flags & 0x80)
    pos = 76
    if flags & 0x0001:  # LinkTargetIDList
        idsz = struct.unpack("<H", data[pos:pos + 2])[0]
        ids = data[pos + 2:pos + 2 + idsz]
        items, i = [], 0
        while i + 2 <= len(ids):
            sz = struct.unpack("<H", ids[i:i + 2])[0]
            if sz == 0:
                break
            items.append(ids[i + 2:i + sz].hex())
            i += sz
        out["id_list"] = items
        pos += 2 + idsz
    if flags & 0x0002:  # LinkInfo
        lsz = struct.unpack("<I", data[pos:pos + 4])[0]
        li = data[pos:pos + lsz]
        hsz = struct.unpack("<I", li[4:8])[0]
        lflags = struct.unpack("<I", li[8:12])[0]
        voff, lboff = struct.unpack("<II", li[12:20])
        rec = {"flags": lflags,
               "local_base_path": _cstr(li[lboff:]) if lboff else ""}
        if voff:
            vol = li[voff:]
            vt, vsz = struct.unpack("<II", vol[:8])
            serial = struct.unpack("<I", vol[8:12])[0]
            laboff = struct.unpack("<I", vol[12:16])[0]
            label = _cstr(vol[laboff:]) if laboff < vsz else ""
            rec["volume"] = {"drive_type":
                             DRIVE_TYPES.get(vt, hex(vt)),
                             "serial": "%08X" % serial,
                             "label": label}
        csuffix = struct.unpack("<I", li[24:28])[0]
        rec["common_suffix"] = _cstr(li[csuffix:]) if csuffix else ""
        if hsz >= 0x24:  # unicode variants present
            lbpu, sfxu = struct.unpack("<II", li[28:36])
            if lbpu:
                rec["local_base_path_u"] = (
                    li[lbpu:].decode("utf-16-le", "replace")
                    .split("\x00")[0])
        pos += lsz
        out["link_info"] = rec
    for bit, key in STRING_FLAGS:
        if not flags & bit:
            continue
        if pos + 2 > len(data):
            break
        n = struct.unpack("<H", data[pos:pos + 2])[0]
        pos += 2
        if uni:
            out[key] = data[pos:pos + n * 2].decode(
                "utf-16-le", "replace")
            pos += n * 2
        else:
            out[key] = data[pos:pos + n].decode("mbcs", "replace")
            pos += n
    if flags & 0x0200 and pos + 4 <= len(data):  # EnvironmentVariable
        bsz = struct.unpack("<I", data[pos:pos + 4])[0]
        blk = data[pos:pos + bsz]
        out["env_var"] = {"ansi": _cstr(blk[4:4 + 260]),
                          "unicode": blk[4 + 260:4 + 260 + 520]
                          .decode("utf-16-le", "replace")
                          .rstrip("\x00")}
    return out


def _selftest():
    # minimal lnk: header + unicode args + LinkInfo with local path
    hdr = bytearray(76)
    hdr[:4] = b"\x4c\x00\x00\x00"
    hdr[4:20] = bytes.fromhex("0114020000000000c000000000000046")
    fl = 0x0002 | 0x0004 | 0x0020 | 0x0080 | 0x0001
    struct.pack_into("<I", hdr, 20, fl)
    struct.pack_into("<QQQ", hdr, 28, 133000000000000000,
                     133000000010000000, 133000000020000000)
    struct.pack_into("<I", hdr, 52, 1234)
    # IDList: one 4-byte item then terminator
    idl = struct.pack("<H", 6) + struct.pack("<HH", 4, 0) + b"\x00\x00"
    # LinkInfo: 7-u32 header, then LocalBasePath + CommonPathSuffix
    lbp = b"C:\\flag\\run.exe\x00"
    sfx = b"run.exe\x00"
    li = struct.pack("<IIIIIII",
                     0x1C + len(lbp) + len(sfx), 0x1C, 1, 0,
                     0x1C, 0, 0x1C + len(lbp))
    li += lbp + sfx
    args = "flag{lnk_args}".encode("utf-16-le")
    body = (idl + li + struct.pack("<H", 5) +
            "name1".encode("utf-16-le") +
            struct.pack("<H", len("flag{lnk_args}")) + args)
    tmp = Path(tempfile.mkdtemp()) / "x.lnk"
    tmp.write_bytes(bytes(hdr) + body)
    out = parse_lnk(tmp)
    assert out.get("arguments") == "flag{lnk_args}", out
    assert out["link_info"]["local_base_path"] == "C:\\flag\\run.exe", out
    assert out["created"] and out["created"].startswith("2022-06-18"), out
    print("lnk_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="decode a .lnk ShellLink to JSON")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    print(json.dumps(parse_lnk(a.file), indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
