#!/usr/bin/env python3
"""mft_parse.py -- parse an extracted $MFT into per-record JSON.

Usage:
  python3 tools/forensics/mft_parse.py MFT                 # all records
  python3 tools/forensics/mft_parse.py MFT --deleted       # !in-use only
  python3 tools/forensics/mft_parse.py MFT --dump 5        # resident $DATA
  python3 tools/forensics/mft_parse.py --selftest

Applies the update-sequence-array fixup, walks the attribute list, and
decodes $STANDARD_INFORMATION (the 4+4 timestamps), $FILE_NAME (parent
ref, own timestamp set, UTF-16 name) and $DATA (resident bytes inline;
non-resident as a cluster runlist). Deleted records keep their bytes
until reused -- a small deleted file is recoverable from the record
itself with no clusters.

Flags field: bit0 = record in use, bit1 = directory. Records failing
the fixup or missing "FILE" are reported as kind=bad only with
--verbose; default output skips them.
"""
import argparse
import json
import struct
import sys
from datetime import datetime, timedelta

EPOCH = datetime(1601, 1, 1)


def _ft(b):
    if len(b) < 8:
        return None
    v = struct.unpack("<Q", b[:8])[0]
    if not v:
        return None
    try:
        return (EPOCH + timedelta(microseconds=v / 10)).isoformat()
    except OverflowError:
        return None


def _fixup(rec):
    """apply USA fixup in place on a mutable record; None if seq bad."""
    if rec[:4] not in (b"FILE", b"BAAD"):
        return None
    uoff, un = struct.unpack("<HH", rec[4:8])
    if not (0x10 <= uoff <= 0x40 and uoff + 2 * un <= len(rec)):
        return None
    seq = bytes(rec[uoff:uoff + 2])
    for i in range(1, un):
        end = i * 512 - 2
        if end + 2 > len(rec):
            break
        if bytes(rec[end:end + 2]) != seq:
            return None
        rec[end:end + 2] = rec[uoff + 2 * i:uoff + 2 * i + 2]
    return rec


def _runlist(buf):
    i, lcn, runs = 0, 0, []
    while i < len(buf) and buf[i]:
        h = buf[i]
        i += 1
        ln, lo = h & 0xF, h >> 4
        if i + ln + lo > len(buf) or ln == 0:
            break
        cnt = int.from_bytes(buf[i:i + ln], "little")
        i += ln
        off = int.from_bytes(buf[i:i + lo], "little", signed=True)
        i += lo
        lcn += off
        runs.append({"lcn": lcn, "clusters": cnt})
    return runs


def _attrs(rec, first):
    off = first
    while off + 8 <= len(rec):
        atype, alen = struct.unpack("<II", rec[off:off + 8])
        if atype == 0xFFFFFFFF or alen < 8 or off + alen > len(rec) + 4:
            break
        yield atype, rec[off:off + alen], bool(rec[off + 8])
        off += alen
        if alen == 0:
            break


def _record(raw, recn):
    rec = _fixup(bytearray(raw))
    if rec is None:
        return None
    seq, _links = struct.unpack("<HH", rec[16:20])
    first, flags = struct.unpack("<HH", rec[20:24])
    out = {"record": recn, "sequence": seq,
           "in_use": bool(flags & 1), "is_dir": bool(flags & 2)}
    for atype, abuf, nonres in _attrs(rec, first):
        nlen, noff = abuf[9], struct.unpack("<H", abuf[10:12])[0]
        aname = abuf[noff:noff + nlen * 2].decode(
            "utf-16-le", "replace") if nlen else ""
        if atype == 0x10 and not nonres:  # $STANDARD_INFORMATION
            clen, coff = struct.unpack("<IH", abuf[16:22])
            c = abuf[coff:coff + clen]
            out["si"] = {"created": _ft(c[0:8]),
                         "modified": _ft(c[8:16]),
                         "mft_changed": _ft(c[16:24]),
                         "accessed": _ft(c[24:32])}
        elif atype == 0x30 and not nonres:  # $FILE_NAME
            clen, coff = struct.unpack("<IH", abuf[16:22])
            c = abuf[coff:coff + clen]
            if len(c) >= 66:
                nlen = c[64]
                name = c[66:66 + nlen * 2].decode("utf-16-le", "replace")
                out.setdefault("names", []).append({
                    "name": name,
                    "parent": struct.unpack("<Q", c[:8])[0] & 0xFFFFFFFFFFFF,
                    "size": struct.unpack("<Q", c[48:56])[0],
                    "created": _ft(c[8:16]),
                     "mft_changed": _ft(c[24:32])})
        elif atype == 0x80:  # $DATA - named streams are ADS payloads
            if nonres:
                roff = struct.unpack("<H", abuf[32:34])[0]
                stream = {"name": aname, "resident": False,
                          "size": struct.unpack("<Q", abuf[48:56])[0],
                          "runs": _runlist(abuf[roff:])}
                if not aname:
                    out["data"] = {k: v for k, v in stream.items()
                                   if k != "name"}
            else:
                clen, coff = struct.unpack("<IH", abuf[16:22])
                body = bytes(abuf[coff:coff + clen])
                stream = {"name": aname, "resident": True,
                          "size": clen,
                          "preview": body[:64].decode("utf-8",
                                                      "replace"),
                          "preview_hex": body[:64].hex()}
                if not aname:
                    out["data"] = {k: v for k, v in stream.items()
                                   if k != "name"}
                    out["_data_bytes"] = body
            if aname:
                out.setdefault("streams", []).append(stream)
    return out


def parse(path, size=1024):
    data = open(path, "rb").read()
    rows, bad = [], 0
    for recn in range(len(data) // size):
        r = _record(data[recn * size:(recn + 1) * size], recn)
        if r is None:
            bad += 1
            continue
        rows.append(r)
    return rows, bad


def _mkrec(flags, attrs, usn=0xAAAA):
    rec = bytearray(1024)
    rec[0:4] = b"FILE"
    uoff = 0x30
    struct.pack_into("<HH", rec, 4, uoff, 3)
    struct.pack_into("<H", rec, uoff, usn)
    for i, end in enumerate((510, 1022)):
        rec[uoff + 2 + 2 * i:uoff + 4 + 2 * i] = rec[end:end + 2]
        rec[end:end + 2] = struct.pack("<H", usn)
    struct.pack_into("<H", rec, 16, 1)      # sequence
    struct.pack_into("<H", rec, 18, 1)      # links
    first = uoff + 8
    struct.pack_into("<H", rec, 20, first)
    struct.pack_into("<H", rec, 22, flags)
    off = first
    for item in attrs:
        atype, content = item[0], item[1]
        name = item[2] if len(item) > 2 else None
        nenc = name.encode("utf-16-le") if name else b""
        alen = 24 + len(nenc) + len(content)
        struct.pack_into("<II", rec, off, atype, alen)
        rec[off + 8] = 0
        rec[off + 9] = len(name or "")
        struct.pack_into("<H", rec, off + 10, 24 if name else 0)
        rec[off + 24:off + 24 + len(nenc)] = nenc
        struct.pack_into("<IH", rec, off + 16, len(content),
                         24 + len(nenc))
        rec[off + 24 + len(nenc):
            off + 24 + len(nenc) + len(content)] = content
        off += alen
    struct.pack_into("<I", rec, off, 0xFFFFFFFF)
    return bytes(rec)


def _selftest():
    import tempfile
    from pathlib import Path
    si = struct.pack("<QQQQ", 133000000000000000, 133000000010000000,
                     133000000020000000, 133000000030000000) + b"\x00" * 40
    nm = "flag.txt".encode("utf-16-le")
    fn = struct.pack("<Q", 5) + si[:32] + struct.pack("<QQ", 44, 44) + \
        struct.pack("<IIBB", 0x20, 0, len(nm), 1) + nm
    body = b"flag{mft_deleted_record}"
    r0 = _mkrec(3, [(0x10, si)])                       # dir, in use
    ads = b"flag{ads_hidden_stream}"
    r5 = _mkrec(0, [(0x10, si), (0x30, fn), (0x80, body),
                    (0x80, ads, "hidden")])
    tmp = Path(tempfile.mkdtemp()) / "MFT"
    tmp.write_bytes(r0 + b"\x00" * 1024 * 4 + r5)
    rows, bad = parse(tmp)
    assert len(rows) == 2 and bad == 4, (len(rows), bad)
    d = rows[1]
    assert not d["in_use"] and not d["is_dir"]
    assert d["names"][0]["name"] == "flag.txt", d["names"]
    assert "flag{mft_deleted_record}" in d["data"]["preview"], \
        d["data"]
    assert "flag{ads_hidden_stream}" in \
        d["streams"][0]["preview"], d["streams"]
    assert d["streams"][0]["name"] == "hidden", d["streams"]
    print("mft_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="parse an extracted $MFT into per-record JSON")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--deleted", action="store_true",
                    help="only records whose in-use flag is clear")
    ap.add_argument("--dump", type=int, metavar="N",
                    help="hex-dump resident $DATA of record N")
    ap.add_argument("--size", type=int, default=1024,
                    help="MFT record size (default 1024)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    rows, bad = parse(a.file, a.size)
    for r in rows:
        if a.deleted and r["in_use"]:
            continue
        body = r.pop("_data_bytes", None)
        if a.dump == r["record"]:
            print((body or b"").hex())
            return
        print(json.dumps(r))
    print(json.dumps({"records": len(rows), "bad": bad}),
          file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
