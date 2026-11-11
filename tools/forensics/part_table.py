#!/usr/bin/env python3
"""part_table.py -- MBR/GPT partition table reader (mmls -t dos|gpt fallback).

Usage:
  python3 tools/forensics/part_table.py image.dd
  python3 tools/forensics/part_table.py image.dd --sector-size 512
  python3 tools/forensics/part_table.py --selftest

MBR: signature 0x55AA @510, four 16-byte entries @0x1BE - status,
CHS first (3B), type byte, CHS last (3B), LBA start u32, sector
count u32. Types 0x05/0x0F/0x85 are extended: each EBR sits at its
own LBA, entry[0] is the logical partition (LBA relative to that
EBR) and entry[1] chains to the next EBR (LBA relative to the
extended base). GPT: protective MBR type 0xEE, header @LBA1
"EFI PART", entries @lba from header+0x48, count @+0x50, entry
size @+0x54 - each entry holds a type GUID, unique GUID,
first/last LBA u64, attrs and a UTF-16LE name.
Feed an offset to a volume reader: fat_read.py <img> --offset
<part.first_lba*512> or use mft_parse on the extracted bytes.
"""
import argparse
import json
import struct
import sys
import tempfile
import uuid
from pathlib import Path

MBR_TYPES = {
    0x00: "empty", 0x01: "FAT12", 0x04: "FAT16<32M", 0x05: "extended",
    0x06: "FAT16", 0x07: "NTFS/exFAT", 0x0B: "FAT32-CHS",
    0x0C: "FAT32-LBA", 0x0E: "FAT16-LBA", 0x0F: "extended-LBA",
    0x27: "WinRE", 0x82: "Linux-swap", 0x83: "Linux",
    0x85: "Linux-extended", 0x8E: "Linux-LVM", 0xA5: "FreeBSD",
    0xA6: "OpenBSD", 0xA8: "macOS", 0xA9: "NetBSD", 0xAF: "HFS+",
    0xEB: "BeOS", 0xEE: "GPT-protective", 0xEF: "EFI-FAT",
}
EXT = {0x05, 0x0F, 0x85}
GPT_TYPES = {
    "c12a7328-f81f-11d2-ba4b-00a0c93ec93b": "EFI-System",
    "e3c9e316-0b5c-4db8-817d-f92df00215ae": "MS-Reserved",
    "ebd0a0a2-b9e5-4433-87c0-68b6b72699c7": "MS-Basic-Data",
    "de94bba4-06d1-4d40-a16a-bfd50179d6ac": "Win-Recovery",
    "0fc63daf-8483-4772-8e79-3d69d8477de4": "Linux-fs",
    "0657fd6d-a4ab-43c4-84e5-0933c84b4f4f": "Linux-swap",
    "4f68bce3-e8cd-4db1-96e7-fbcaf984b709": "Linux-RAID",
    "e6d6d379-f507-44c2-a23c-238f2a3df928": "Linux-LVM",
    "48465300-0000-11aa-aa11-00306543ecac": "Apple-HFS+",
    "516e7cb4-6ecf-11d6-8ff8-00022d09712b": "FreeBSD-FFS",
}


def _mbr_entries(d, off):
    """Yield the four raw partition entries at byte offset off."""
    for i in range(4):
        e = d[off + 0x1BE + i * 16: off + 0x1BE + i * 16 + 16]
        if len(e) == 16:
            yield e


def _gpt(d, ss):
    if len(d) < 2 * ss or d[ss:ss + 8] != b"EFI PART":
        return None
    ent_lba = struct.unpack("<Q", d[ss + 0x48:ss + 0x50])[0]
    cnt = struct.unpack("<I", d[ss + 0x50:ss + 0x54])[0]
    esz = struct.unpack("<I", d[ss + 0x54:ss + 0x58])[0]
    parts = []
    for i in range(min(cnt, 4096)):
        e = d[ent_lba * ss + i * esz: ent_lba * ss + i * esz + esz]
        if len(e) < esz or e[:16] == b"\x00" * 16:
            continue
        tguid = str(uuid.UUID(bytes_le=e[:16]))
        parts.append({
            "index": i + 1, "scheme": "gpt",
            "type_guid": tguid,
            "type_name": GPT_TYPES.get(tguid, "unknown"),
            "unique_guid": str(uuid.UUID(bytes_le=e[16:32])),
            "first_lba": struct.unpack("<Q", e[32:40])[0],
            "last_lba": struct.unpack("<Q", e[40:48])[0],
            "sectors": struct.unpack("<Q", e[40:48])[0]
            - struct.unpack("<Q", e[32:40])[0] + 1,
            "offset": struct.unpack("<Q", e[32:40])[0] * ss,
            "name": e[56:128].decode("utf-16-le", "replace")
            .split("\x00")[0]})
    return parts


def partitions(d, ss=512):
    parts = _gpt(d, ss)
    if parts is not None:
        return "gpt", parts
    if len(d) < 512 or d[510:512] != b"\x55\xaa":
        return "unknown", []
    out, stack, seen, idx = [], [0], set(), 0
    ebr_base = 0
    while stack and idx < 128:
        base = stack.pop(0)
        if base in seen or base * ss + 512 > len(d):
            continue
        seen.add(base)
        for e in _mbr_entries(d, base * ss):
            ptype, lba, secs = e[4], struct.unpack("<I", e[8:12])[0], \
                struct.unpack("<I", e[12:16])[0]
            if ptype == 0 or secs == 0:
                continue
            if ptype in EXT:
                if base == 0:
                    ebr_base = lba          # extended base for chaining
                    stack.append(ebr_base)
                else:
                    stack.append(ebr_base + lba)
                continue
            idx += 1
            start = base + lba if base else lba
            out.append({
                "index": idx, "scheme": "mbr",
                "type": f"0x{ptype:02x}",
                "type_name": MBR_TYPES.get(ptype, "unknown"),
                "first_lba": start, "sectors": secs,
                "offset": start * ss,
                "bootable": bool(e[0] & 0x80)})
    return "mbr", out


def _selftest():
    ss = 512
    # MBR disk: FAT32 @2048x4096 bootable + extended -> NTFS logical
    mbr = bytearray(8192 * ss)
    mbr[510:512] = b"\x55\xaa"
    def mbr_e(i, ptype, lba, secs, boot=0, base=0):
        e = bytearray(16)
        e[0] = boot
        e[4] = ptype
        struct.pack_into("<I", e, 8, lba)
        struct.pack_into("<I", e, 12, secs)
        mbr[base + 0x1BE + i * 16:base + 0x1BE + i * 16 + 16] = e
    mbr_e(0, 0x0C, 2048, 4096, boot=0x80)
    mbr_e(1, 0x0F, 6144, 2048)
    # EBR @6144: logical NTFS rel 2048, no next
    mbr_e(0, 0x07, 2048, 1024, base=6144 * ss)
    scheme, parts = partitions(bytes(mbr), ss)
    assert scheme == "mbr", scheme
    assert len(parts) == 2, parts
    assert parts[0]["type_name"] == "FAT32-LBA" and \
        parts[0]["bootable"] and parts[0]["offset"] == 2048 * ss, parts
    assert parts[1]["type_name"] == "NTFS/exFAT" and \
        parts[1]["first_lba"] == 6144 + 2048, parts
    # GPT disk: protective MBR + header + 2 entries
    gpt = bytearray(4096 * ss)
    mbr_e(0, 0xEE, 1, 4095)
    gpt[ss:ss + 8] = b"EFI PART"
    struct.pack_into("<Q", gpt, ss + 0x48, 2)      # entries @ LBA2
    struct.pack_into("<I", gpt, ss + 0x50, 128)
    struct.pack_into("<I", gpt, ss + 0x54, 128)
    def gpt_e(i, tguid, first, last, name):
        e = bytearray(128)
        e[:16] = uuid.UUID(tguid).bytes_le
        e[16:32] = uuid.uuid4().bytes_le
        struct.pack_into("<Q", e, 32, first)
        struct.pack_into("<Q", e, 40, last)
        e[56:56 + len(name) * 2] = name.encode("utf-16-le")
        gpt[2 * ss + i * 128:2 * ss + i * 128 + 128] = e
    gpt_e(0, "c12a7328-f81f-11d2-ba4b-00a0c93ec93b", 2048, 4095,
          "EFI system")
    gpt_e(1, "0fc63daf-8483-4772-8e79-3d69d8477de4", 4096, 8191,
          "rootfs")
    scheme, parts = partitions(bytes(gpt), ss)
    assert scheme == "gpt" and len(parts) == 2, parts
    assert parts[0]["type_name"] == "EFI-System" and \
        parts[0]["name"] == "EFI system", parts
    assert parts[1]["type_name"] == "Linux-fs" and \
        parts[1]["sectors"] == 4096, parts
    print("part_table selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="list MBR/GPT partitions (mmls fallback)")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--sector-size", type=int, default=512)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    d = Path(a.file).read_bytes()
    scheme, parts = partitions(d, a.sector_size)
    print(json.dumps({"scheme": scheme, "sector_size": a.sector_size,
                      "partitions": parts}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
