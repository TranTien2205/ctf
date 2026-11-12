#!/usr/bin/env python3
"""ntfs_indx.py -- $I30 index-record scanner: deleted filenames.

`mft_parse` reads live $FILE_NAME attributes; the $I30 index blocks
($INDEX_ROOT inside a directory record, $INDEX_ALLOCATION slabs, or
carved INDX pages) keep SLACK entries for names that were deleted --
the standard "what was deleted here" question in Sherlocks. An INDX
page is: 'INDX' + update-seq fields + index header + entries. Each
entry: file ref(8) + entry size(2) + stream size(2) + flags(4) +
a $FILE_NAME attribute (parent ref, times, sizes, name len, namespace,
UTF-16 name). This tool scans any blob for INDX pages, walks entries
through slack space, and reports every filename with its timestamps
-- live and slack alike, marked by where they were found.

  python3 tools/forensics/ntfs_indx.py image.dd --offset 0x4000
  python3 tools/forensics/ntfs_indx.py indx_carve.bin
  python3 tools/forensics/ntfs_indx.py --selftest
"""
import argparse
import json
import struct
import sys

EPOCH = 11644473600          # FILETIME epoch delta to unix seconds


def _ft(v):
    import datetime
    if not v or v > 0x7FFFFFFFFFFFFFFF:
        return "1970-01-01"
    try:
        return datetime.datetime.fromtimestamp(
            v // 10000000 - EPOCH, datetime.timezone.utc).strftime(
            "%Y-%m-%d %H:%M:%S")
    except (OSError, OverflowError, ValueError):
        return "bad:%x" % v


def _fname(buf, off):
    """parse a $FILE_NAME attr body at off; return (dict, next) or None."""
    if off + 66 > len(buf):
        return None
    parent = struct.unpack("<Q", buf[off:off + 8])[0] & 0xFFFFFFFFFFFF
    cr, mod, _mft, acc = struct.unpack("<4Q", buf[off + 8:off + 40])
    _alloc, real = struct.unpack("<2Q", buf[off + 40:off + 56])
    flags = struct.unpack("<I", buf[off + 56:off + 60])[0]
    nlen = buf[off + 64]
    ns = buf[off + 65]
    if nlen == 0 or nlen > 255 or off + 66 + nlen * 2 > len(buf):
        return None
    name = buf[off + 66:off + 66 + nlen * 2].decode(
        "utf-16-le", "replace")
    return ({"name": name, "parent_mft": parent, "namespace": ns,
             "real_size": real, "flags": hex(flags),
             "created": _ft(cr), "modified": _ft(mod),
             "accessed": _ft(acc)}, nlen)


def scan(data, base=0):
    """scan a blob for INDX pages and walk their entry arrays."""
    out = []
    pos = 0
    while True:
        pos = data.find(b"INDX", pos)
        if pos < 0 or pos + 0x30 > len(data):
            break
        # INDX page header: usa_off(2) usa_cnt(2) lsn(8) vcn(8)
        usa_off, usa_cnt = struct.unpack("<HH", data[pos + 4:pos + 8])
        if not (0 < usa_off < 0x30 and 0 < usa_cnt < 100):
            pos += 4
            continue
        hdr = pos + 0x18
        entries_off, _free_off, _end, _sz = struct.unpack(
            "<IIII", data[hdr:hdr + 16])
        e = hdr + 0x18 + entries_off
        page_end = pos + 0x1000 if pos + 0x1000 <= len(data) \
            else len(data)
        chain_end = None
        while e + 16 <= page_end:
            ref, esize, ssize, eflags = struct.unpack(
                "<QHHI", data[e:e + 16])
            if esize == 0 or esize > 0x400:
                break
            ent = _fname(data, e + 16)
            last = bool(eflags & 2)
            sub = bool(eflags & 1)
            if ent:
                rec = ent[0]
                rec["mft_ref"] = ref & 0xFFFFFFFFFFFF
                rec["indx_page"] = hex(base + pos)
                rec["entry_off"] = hex(e)
                rec["last_entry"] = last
                if sub:
                    rec["has_subnode"] = True
                out.append(rec)
            e += esize
            if last:
                chain_end = e
                break
        # slack scan: deleted entries survive as orphaned bytes in the
        # free region after the live chain ends
        if chain_end is not None:
            s = chain_end
            while s + 16 <= page_end:
                ref, esize, ssize, eflags = struct.unpack(
                    "<QHHI", data[s:s + 16])
                if (16 <= esize <= 0x200 and eflags & 0xFFFFFFFC == 0
                        and not (eflags & 2)):
                    ent = _fname(data, s + 16)
                    if ent and all(32 <= ord(c) < 127 or ord(c) >= 128
                                   for c in ent[0]["name"]):
                        rec = ent[0]
                        rec["mft_ref"] = ref & 0xFFFFFFFFFFFF
                        rec["indx_page"] = hex(base + pos)
                        rec["entry_off"] = hex(s)
                        rec["slack"] = True
                        out.append(rec)
                        s += esize
                        continue
                s += 8
        pos += 4
    return out


def _selftest():
    def fname(parent, name, cr=133500000000000000, real=17):
        nb = name.encode("utf-16-le")
        a = struct.pack("<Q", parent) + struct.pack("<4Q", cr, cr, 0, cr)
        a += struct.pack("<2Q", real, real) + struct.pack("<I", 0x20)
        a += struct.pack("<I", 0) + bytes([len(nb) // 2, 1]) + nb
        return a
    def entry(ref, body, flags=0, pad=8):
        esize = 16 + len(body)
        esize = (esize + 7) & ~7
        e = struct.pack("<QHHI", ref, esize, len(body), flags) + body
        return e + b"\x00" * (esize - 16 - len(body))
    page = bytearray(0x1000)
    page[:4] = b"INDX"
    struct.pack_into("<HH", page, 4, 0x28, 3)
    # header at +0x18: entries_off, free_off, end_off, size
    e1 = entry(0x2A, fname(5, "live.txt"))
    e2 = entry(0x2B, fname(5, "flag_del.txt"))
    e3 = entry(0, b"", flags=2)
    struct.pack_into("<IIII", page, 0x18, 0, 0,
                     len(e1 + e2 + e3) + 0x18, 0)
    page[0x30:0x30 + len(e1 + e2 + e3)] = e1 + e2 + e3
    # a slack entry past the END marker: carve it manually
    slack = entry(0x2C, fname(5, "flag{deleted_name}"))
    page[0x400:0x400 + len(slack)] = slack
    recs = scan(bytes(page))
    names = {r["name"] for r in recs}
    assert "live.txt" in names and "flag_del.txt" in names, names
    assert "flag{deleted_name}" in names, names
    by = {r["name"]: r for r in recs}
    assert by["live.txt"]["mft_ref"] == 0x2A
    assert by["flag{deleted_name}"]["indx_page"] == "0x0"
    print("ntfs_indx selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="$I30 INDX record scanner")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--offset", type=lambda x: int(x, 0), default=0,
                    help="base offset for reported page addresses")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    recs = scan(data, a.offset)
    print(json.dumps({"records": recs, "count": len(recs)}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
