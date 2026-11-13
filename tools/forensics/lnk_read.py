#!/usr/bin/env python3
"""lnk_read.py -- Windows .lnk shortcut parser.

`lnk` artifacts appear in KAPE bundles and Sherlocks: recent files a
user opened, pinned items, startup entries. The format is documented:
a 0x4C SHELL_LINK_HEADER (link flags, attributes, three FILETIMEs,
icon/target/dos strings), an optional LinkTargetIDList, an optional
LinkInfo block carrying the resolved volume + local_base_path, and
trailing string data (name/relative/working-dir/args/icon-loc). This
recovers the target path, the drive type and serial, the timestamps
and any working-dir/args without `LnkParse3`/`lecmd`.

  python3 tools/forensics/lnk_read.py file.lnk
  python3 tools/forensics/lnk_read.py --selftest
"""
import argparse
import json
import struct
import sys
import datetime

LNK_SIG = b"L\x00\x00\x00\x01\x14\x02\x00\x00\x00\x00\x00\xc0\x00\x00\x00\x00\x00\x00\x46"

DRIVE = {2: "removable", 3: "fixed", 4: "network", 5: "cdrom", 6: "ramdisk"}
FLAG_NAMES = {0x01: "HasIDList", 0x02: "HasLinkInfo", 0x04: "HasName",
              0x08: "HasRelative", 0x10: "HasWorkDir", 0x20: "HasArgs",
              0x40: "HasIconLoc", 0x80: "IsUnicode", 0x200: "HasExpIcon",
              0x20000: "RunAsUser", 0x1000000: "HasDarwinID",
              0x2000000: "RunAsIcon", 0x8000000: "HasIconEnv"}


def _ft(v):
    try:
        return (datetime.datetime(1601, 1, 1) + datetime.timedelta(
            microseconds=v / 10)).isoformat()
    except (OverflowError, OSError, ValueError):
        return "0x%x" % v


def parse(data):
    if len(data) < 76 or data[:20] != LNK_SIG:
        return {"error": "not a .lnk (SHELL_LINK_HEADER signature)"}
    flags, = struct.unpack("<I", data[20:24])
    ctime, atime, mtime = struct.unpack("<QQQ", data[28:52])
    size, = struct.unpack("<I", data[52:56])
    uni = flags & 0x80
    pos = 76
    out = {"size_bytes": size,
           "created": _ft(ctime), "accessed": _ft(atime),
           "modified": _ft(mtime),
           "flags": [n for b, n in FLAG_NAMES.items() if flags & b]}
    if flags & 0x01:                             # LinkTargetIDList
        if pos + 2 > len(data):
            out["error"] = "truncated idlist size"
            return out
        sz, = struct.unpack("<H", data[pos:pos + 2])
        out["idlist_bytes"] = sz
        pos += 2 + sz
    if flags & 0x02:                             # LinkInfo
        if pos + 4 > len(data):
            out["error"] = "truncated linkinfo"
            return out
        lisz, = struct.unpack("<I", data[pos:pos + 4])
        li = data[pos:pos + lisz]
        # 0 sz | 4 head_sz | 8 li_flags | c vol_id_off | 10 lbp_off |
        # 14 cnrl_off | 18 cps_off | [1c lbp_u | 20 cps_u if head>=0x24]
        if len(li) >= 0x1c:
            head_sz, li_fl, vid_off, lbp_off = struct.unpack(
                "<IIII", li[4:20])
            cps_off, = struct.unpack("<I", li[0x18:0x1c])
            def _sz(off):
                if not off or off >= len(li):
                    return None
                e = li.find(b"\x00", off)
                return li[off:e].decode("latin-1", "replace") if e > 0 else None
            info = {"local_base_path": _sz(lbp_off),
                    "common_path_suffix": _sz(cps_off)}
            if vid_off and vid_off + 16 <= len(li):
                _, drive, serial, lab_off = struct.unpack(
                    "<IIII", li[vid_off:vid_off + 16])
                info["drive_type"] = DRIVE.get(drive, str(drive))
                info["volume_serial"] = "%08x" % serial
                if 0 < lab_off < 0x14:
                    info["volume_label"] = _sz(vid_off + lab_off)
                # lab_off==0x14 -> unicode label, offset at vid_off+16
                elif lab_off == 0x14 and vid_off + 20 <= len(li):
                    uoff, = struct.unpack("<I", li[vid_off + 16:vid_off + 20])
                    info["volume_label_unicode_off"] = uoff
            if head_sz >= 0x24 and len(li) >= 0x24:
                lbp_u, = struct.unpack("<I", li[0x1c:0x20])
                if lbp_u and lbp_u + 2 <= len(li):
                    e = li.find(b"\x00\x00", lbp_u)
                    if e > 0:
                        info["local_base_path_unicode"] = li[lbp_u:e].decode(
                            "utf-16-le", "replace")
            if not (li_fl & 1):
                info["note"] = "VolumeIDAndLocalBasePath flag clear"
            out["linkinfo"] = info
        pos += lisz
    # trailing string data (count16 + chars)
    def _str(p):
        if p + 2 > len(data):
            return None, p
        n, = struct.unpack("<H", data[p:p + 2])
        if uni:
            s = data[p + 2:p + 2 + n * 2].decode("utf-16-le", "replace")
            return s, p + 2 + n * 2
        s = data[p + 2:p + 2 + n].decode("latin-1", "replace")
        return s, p + 2 + n
    for bit, key in ((0x04, "name"), (0x08, "relative_path"),
                     (0x10, "working_dir"), (0x20, "args"),
                     (0x40, "icon_location")):
        if flags & bit:
            s, pos = _str(pos)
            out[key] = s
    return out


def _selftest():
    hdr = LNK_SIG
    hdr += struct.pack("<I", 0x02 | 0x80 | 0x10 | 0x20)
    hdr += struct.pack("<I", 0)                # file attrs
    hdr += struct.pack("<QQQ", 133485000000000000,
                        133485000000000000, 133485000000000000)
    hdr += struct.pack("<I", 1234)             # target size
    hdr += b"\x00" * (76 - len(hdr))           # pad header
    # LinkInfo: [sz][head=0x24][li_fl=1][vid_off][lbp_off][cnrl=0]
    #           [cps_off][lbp_u=0][cps_u=0] | VolumeID | lbp | cps
    lbp = b"C:\\Users\\x\\flag.docx\x00"
    cps = b"flag.docx\x00"
    vol = struct.pack("<IIII", 20, 3, 0xA1B2C3D4, 0x14) \
        + struct.pack("<I", 0)                 # unicode label off
    head_sz = 0x24
    vid_off = head_sz
    lbp_off = vid_off + len(vol)
    cps_off = lbp_off + len(lbp)
    li_sz = cps_off + len(cps)
    li = struct.pack("<IIIIIIIII", li_sz, head_sz, 1, vid_off,
                     lbp_off, 0, cps_off, 0, 0) + vol + lbp + cps
    # trailing string data: working_dir + args (unicode, flags set)
    wd = "C:\\Users\\x".encode("utf-16-le")
    args = "--open flag.docx".encode("utf-16-le")
    tail = struct.pack("<H", len(wd) // 2) + wd \
        + struct.pack("<H", len(args) // 2) + args
    body = hdr + li + tail
    out = parse(body)
    assert out.get("linkinfo", {}).get("drive_type") == "fixed", out
    assert out["linkinfo"]["local_base_path"] == \
        "C:\\Users\\x\\flag.docx", out
    assert out["linkinfo"]["volume_serial"] == "a1b2c3d4", out
    assert out["linkinfo"]["common_path_suffix"] == "flag.docx", out
    assert out["working_dir"] == "C:\\Users\\x", out
    assert out["args"] == "--open flag.docx", out
    assert out["size_bytes"] == 1234
    assert "HasLinkInfo" in out["flags"]
    print("lnk_read selftest: ok")


def main():
    ap = argparse.ArgumentParser(description=".lnk shortcut parser")
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
