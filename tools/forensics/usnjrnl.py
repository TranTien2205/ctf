#!/usr/bin/env python3
"""usnjrnl.py -- $UsnJrnl:$J change-journal record reader.

`$Extend/$UsnJrnl:$J` in a KAPE triage or an extracted $J stream is
the closest thing Windows has to an inotify log: one record per
filesystem change (create/write/rename/delete/security) on every
file. Records are self-delimiting (RecordLength first u32) and
versions 2/4 share the useful fields: file + parent MFT references,
USN, FILETIME stamp, reason and source flags, and a UTF-16 name.
This walks a $J stream, decodes the reason bits to names, and
emits a JSON timeline; `--grep PAT` keeps only matching names.
Sparse-region zero pages in the stream are skipped honestly.

  python3 tools/forensics/usnjrnl.py 'UsnJrnl.bin' --grep flag
  python3 tools/forensics/usnjrnl.py --selftest
"""
import argparse
import datetime
import json
import struct

REASON = [(0x00000001, "DataOverwrite"), (0x00000002, "DataExtend"),
          (0x00000004, "DataTruncation"), (0x00000010, "NamedDataOverwrite"),
          (0x00000020, "NamedDataExtend"), (0x00000040, "NamedDataTruncation"),
          (0x00000100, "FileCreate"), (0x00000200, "FileDelete"),
          (0x00000400, "EaChange"), (0x00000800, "SecurityChange"),
          (0x00001000, "RenameOldName"), (0x00002000, "RenameNewName"),
          (0x00004000, "IndexableChange"), (0x00008000, "BasicInfoChange"),
          (0x00010000, "HardLinkChange"), (0x00020000, "CompressionChange"),
          (0x00040000, "EncryptionChange"), (0x00080000, "ObjectIdChange"),
          (0x00100000, "ReparsePointChange"), (0x00200000, "StreamChange"),
          (0x80000000, "Close")]


def _ft(v):
    try:
        return (datetime.datetime(1601, 1, 1) + datetime.timedelta(
            microseconds=v / 10)).isoformat()
    except (OverflowError, OSError, ValueError):
        return "0x%x" % v


def _reason(v):
    return [n for b, n in REASON if v & b]


def records(data):
    """Walk a raw $J stream; skip zero-fill pages."""
    out = []
    pos = 0
    n = len(data)
    while pos + 8 <= n:
        # zero-fill regions between sparse extents: scan ahead for a
        # plausible RecordLength (4..1MB, followed by VersionMajor 2/4)
        rlen, vmaj = struct.unpack("<IH", data[pos:pos + 6])
        if rlen < 4 or rlen > 0x100000 or vmaj not in (2, 4):
            # skip to next non-zero byte
            nxt = pos + 1
            while nxt < n and data[nxt] == 0:
                nxt += 1
            pos = nxt if nxt != pos + 1 else pos + 1
            continue
        rec = data[pos:pos + rlen]
        if len(rec) < rlen:
            break
        if vmaj == 2:
            # minor(2) fileref(8) parentref(8) usn(8) time(8)
            # reason(4) source(4) secid(4) fattr(4) nlen(2) noff(2)
            try:
                (fr, pf, usn, ts, reason, src, _sec, fattr,
                 nlen, noff) = struct.unpack("<QQQQIIIIHH", rec[8:60])
            except struct.error:
                pos += 4
                continue
            name = rec[noff:noff + nlen].decode("utf-16-le", "replace") \
                if noff + nlen <= len(rec) else ""
            out.append({"version": 2, "record_len": rlen,
                        "file_ref": fr & 0xFFFFFFFFFFFF,
                        "parent_ref": pf & 0xFFFFFFFFFFFF,
                        "usn": usn, "time": _ft(ts), "reason": hex(reason),
                        "reason_names": _reason(reason),
                        "source": hex(src), "file_attr": hex(fattr),
                        "name": name})
            pos += rlen
        else:                                    # v4: adds extents
            try:
                (fr, pf, usn, ts, reason, src, _sec, fattr,
                 nlen, noff, _nex, _xoff) = struct.unpack(
                    "<QQQQIIIIHHHH", rec[8:64])
            except struct.error:
                pos += 4
                continue
            name = rec[noff:noff + nlen].decode("utf-16-le", "replace") \
                if noff + nlen <= len(rec) else ""
            out.append({"version": 4, "record_len": rlen,
                        "file_ref": fr & 0xFFFFFFFFFFFF,
                        "parent_ref": pf & 0xFFFFFFFFFFFF,
                        "usn": usn, "time": _ft(ts), "reason": hex(reason),
                        "reason_names": _reason(reason),
                        "name": name})
            pos += rlen
    return out


def _selftest():
    def rec(usn, reason, name, ver=2):
        nb = name.encode("utf-16-le")
        rlen = 60 + len(nb)
        rlen = (rlen + 7) & ~7
        body = struct.pack("<IH", rlen, ver) + b"\x00\x00" \
            + struct.pack("<QQQQIIIIHH", 0x1111, 0x2222, usn,
                          133485000000000000, reason, 0, 0, 0x20,
                          len(nb), 60)
        body += nb + b"\x00" * (rlen - 60 - len(nb))
        return body
    stream = b"\x00" * 64 \
        + rec(0x1000, 0x00000100 | 0x80000000, "flag.txt") \
        + rec(0x1008, 0x00001000 | 0x00002000, "flag.txt") \
        + b"\x00" * 16 \
        + rec(0x2000, 0x00000200, "evil.exe")
    out = records(stream)
    assert len(out) == 3, out
    assert out[0]["name"] == "flag.txt"
    assert "FileCreate" in out[0]["reason_names"]
    assert "Close" in out[0]["reason_names"]
    assert out[1]["usn"] == 0x1008
    assert "RenameNewName" in out[1]["reason_names"]
    assert out[2]["name"] == "evil.exe"
    assert "FileDelete" in out[2]["reason_names"]
    print("usnjrnl selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="$UsnJrnl:$J reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--grep")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    out = records(open(a.path, "rb").read())
    if a.grep:
        g = a.grep.lower()
        out = [r for r in out if g in r.get("name", "").lower()]
    print(json.dumps({"records": out, "count": len(out)}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
