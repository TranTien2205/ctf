#!/usr/bin/env python3
"""evtx_parse.py -- decode .evtx records to XML with no external tools.

Usage:
  python3 tools/forensics/evtx_parse.py FILE.evtx            # XML records
  python3 tools/forensics/evtx_parse.py FILE.evtx --strings  # also UTF-16 dump
  python3 tools/forensics/evtx_parse.py --selftest

Implements the documented EVTX structures directly:
  file header "ElfFile" -> 64 KiB chunks "ElfChnk" -> event records
  (signature 2A 2A 00 00, size, record id, written FILETIME, BinXML).
BinXML tokens per MS-EVEN6: fragment header 0x0F, element start
0x01/0x41 (u16 dependency, u32 size, u32 chunk-relative name offset,
u32 attribute-list size), attribute 0x06/0x46, value 0x05/0x45,
template instance 0x0C with the 33-byte definition header and a
per-record substitution descriptor array, substitutions 0x0D/0x0E,
plus value types 0x00-0x15/0x21 and the 0x80 array bit.

Coverage honest notes: template definitions embedded in the record or
shared at chunk offsets are both handled; WEVT_TEMPLATE resources in PE
files are out of scope. The decode is best-effort per record - a bad
record is reported on stderr and skipped, never fatal.
"""
import argparse
import json
import struct
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

MAGIC = b"ElfFile\x00"
CHUNK_MAGIC = b"ElfChnk\x00"
REC_MAGIC = b"\x2a\x2a\x00\x00"
CHUNK = 0x10000
EPOCH = datetime(1601, 1, 1)
ESC = {"&": "&amp;", "<": "&lt;", ">": "&gt;",
       '"': "&quot;", "'": "&apos;"}
VALUE_TOKENS = {0x05, 0x0D, 0x0E, 0x08, 0x09, 0x07}


def _esc(s):
    return "".join(ESC.get(c, c) for c in s)


def _ft(b):
    v = struct.unpack("<Q", b[:8])[0]
    if not v or v > 0x8000000000000000:
        return ""
    try:
        return (EPOCH + timedelta(microseconds=v / 10)).isoformat() + "Z"
    except OverflowError:
        return ""


def _guid(b):
    if len(b) < 16:
        return b.hex()
    d1, d2, d3 = struct.unpack("<IHH", b[:8])
    return "%08x-%04x-%04x-%s-%s" % (
        d1, d2, d3, b[8:10].hex(), b[10:16].hex())


class _Dec:
    """One chunk + the substitution values of the instance being decoded."""

    def __init__(self, chunk):
        self.chunk = chunk
        self.subs = []

    def name(self, off):
        if off <= 0 or off + 8 > len(self.chunk):
            return None
        cnt = struct.unpack("<H", self.chunk[off + 6:off + 8])[0]
        if off + 8 + cnt * 2 > len(self.chunk):
            return None
        raw = self.chunk[off + 8:off + 8 + cnt * 2]
        return raw.decode("utf-16-le", "replace").rstrip("\x00")

    def value(self, pos, vtype, size):
        """-> (text, next_pos). size < 0 means framed (u16/u32 prefix)."""
        b = self.chunk
        arr = bool(vtype & 0x80)
        t = vtype & 0x7F
        if t == 0x00:
            return "", pos
        fixed = {0x03: ("b", 1), 0x04: ("B", 1), 0x05: ("h", 2),
                 0x06: ("H", 2), 0x07: ("i", 4), 0x08: ("I", 4),
                 0x09: ("q", 8), 0x0A: ("Q", 8), 0x0B: ("f", 4),
                 0x0C: ("d", 8), 0x14: ("I", 4), 0x15: ("Q", 8)}
        if arr:
            if t in (0x01, 0x02):
                n = size if size >= 0 else 0
                enc = "utf-16-le" if t == 1 else "latin-1"
                raw = b[pos:pos + n]
                parts = [p for p in raw.decode(enc, "replace")
                         .split("\x00") if p]
                return ", ".join(parts), pos + n
            sz = {0x03: 1, 0x04: 1, 0x05: 2, 0x06: 2, 0x07: 4,
                  0x08: 4, 0x09: 8, 0x0A: 8, 0x0B: 4, 0x0C: 4,
                  0x0D: 4, 0x0F: 16, 0x11: 8, 0x12: 16,
                  0x14: 4, 0x15: 8}.get(t)
            if not sz:
                return "", pos
            n = size if size >= 0 else sz
            out, p = [], pos
            while p + sz <= pos + n:
                v, p2 = self.value(p, t, sz)
                out.append(v)
                p = p2
            return ", ".join(out), pos + n
        if t in fixed:
            fmt, sz2 = fixed[t]
            if pos + sz2 > len(b):
                return "", pos + sz2
            v = struct.unpack("<" + fmt, b[pos:pos + sz2])[0]
            if t in (0x14, 0x15):
                return hex(v), pos + sz2
            return str(v), pos + sz2
        if t == 0x0D:
            v = struct.unpack("<I", b[pos:pos + 4])[0]
            return "true" if v else "false", pos + 4
        if t in (0x01, 0x02):
            if size < 0:
                n = struct.unpack("<H", b[pos:pos + 2])[0]
                pos += 2
            else:
                n = size // (2 if t == 1 else 1)
            enc = "utf-16-le" if t == 1 else "latin-1"
            raw = b[pos:pos + n * (2 if t == 1 else 1)]
            return raw.decode(enc, "replace"), pos + len(raw)
        if t == 0x0E:
            n = size if size >= 0 else struct.unpack(
                "<I", b[pos:pos + 4])[0]
            pos0 = pos if size >= 0 else pos + 4
            return "0x" + b[pos0:pos0 + n].hex(), pos0 + n
        if t == 0x0F:
            return _guid(b[pos:pos + 16]), pos + 16
        if t == 0x10:
            n = size if size >= 0 else 4
            return str(int.from_bytes(b[pos:pos + n], "little")), pos + n
        if t == 0x11:
            return _ft(b[pos:pos + 8]), pos + 8
        if t == 0x12:
            y, mo, _dow, d, h, mi, s, ms = struct.unpack(
                "<8H", b[pos:pos + 16])
            return ("%04d-%02d-%02dT%02d:%02d:%02d.%03dZ"
                    % (y, mo, d, h, mi, s, ms)), pos + 16
        if t == 0x13:
            if pos + 8 > len(b):
                return "", pos
            cnt = b[pos + 1]
            auth = int.from_bytes(b[pos + 2:pos + 8], "big")
            subs = []
            p = pos + 8
            for _ in range(cnt):
                subs.append(str(struct.unpack("<I", b[p:p + 4])[0]))
                p += 4
            return "S-%d-%d-%s" % (b[pos], auth, "-".join(subs)), p
        if t == 0x21:
            n = size if size >= 0 else struct.unpack(
                "<I", b[pos:pos + 4])[0]
            p0 = pos if size >= 0 else pos + 4
            sub = _Dec(b)
            sub.subs = self.subs
            try:
                xml = sub.decode(p0, p0 + n)
            except Exception:
                xml = "0x" + b[p0:p0 + n].hex()
            return xml, p0 + n
        return "", pos

    def decode(self, pos, end=None):
        """Decode a BinXML fragment stream starting at pos -> XML text."""
        b = self.chunk
        out, stack, suppress = [], [], 0
        end = len(b) if end is None else end
        while pos < end:
            tok = b[pos]
            t, more = tok & 0x3F, bool(tok & 0x40)
            if t == 0x00:
                return "".join(out)
            if t == 0x0F:
                pos += 4
                continue
            if t == 0x01:
                dep = struct.unpack("<H", b[pos + 1:pos + 3])[0]
                noff = struct.unpack("<I", b[pos + 7:pos + 11])[0]
                name = self.name(noff) or "?"
                pos += 11
                dead = (dep != 0xFFFF and dep < len(self.subs)
                        and self.subs[dep][1] == 0x00)
                if dead:
                    suppress = 1
                    stack.append(name)
                elif suppress:
                    suppress += 1
                    stack.append(name)
                else:
                    out.append("<" + name)
                    stack.append(name)
                if more:
                    alen = struct.unpack("<I", b[pos:pos + 4])[0]
                    pos += 4
                    aend = pos + alen
                    while pos < aend and (b[pos] & 0x3F) == 0x06:
                        pos = self._attr(pos, out, suppress)
                    pos = aend
                continue
            if t == 0x02:
                if not suppress:
                    out.append(">")
                pos += 1
                continue
            if t == 0x03:
                name = stack.pop() if stack else "?"
                if not suppress:
                    out.append("/>")
                elif suppress == 1:
                    suppress = 0
                pos += 1
                continue
            if t == 0x04:
                name = stack.pop() if stack else "?"
                if suppress:
                    suppress -= 1
                else:
                    out.append("</" + name + ">")
                pos += 1
                continue
            if suppress:
                pos = self._skip(pos, end)
                continue
            if t == 0x05:
                v, pos = self.value(pos + 2, b[pos + 1], -1)
                out.append(_esc(v))
                continue
            if t == 0x07:
                n = struct.unpack("<I", b[pos + 1:pos + 5])[0]
                out.append("<![CDATA[" + b[pos + 5:pos + 5 + n]
                           .decode("utf-8", "replace") + "]]>")
                pos += 5 + n
                continue
            if t == 0x08:
                out.append("&#x%x;" % struct.unpack(
                    "<H", b[pos + 1:pos + 3])[0])
                pos += 3
                continue
            if t == 0x09:
                noff = struct.unpack("<I", b[pos + 1:pos + 5])[0]
                out.append("&" + (self.name(noff) or "?") + ";")
                pos += 5
                continue
            if t == 0x0A:
                noff = struct.unpack("<I", b[pos + 1:pos + 5])[0]
                out.append("<?" + (self.name(noff) or "?"))
                pos += 5
                continue
            if t == 0x0B:
                n = struct.unpack("<I", b[pos + 1:pos + 5])[0]
                out.append(b[pos + 5:pos + 5 + n]
                           .decode("utf-8", "replace") + "?>")
                pos += 5 + n
                continue
            if t == 0x0C:
                pos = self._instance(pos, out)
                continue
            if t in (0x0D, 0x0E):
                idx = struct.unpack("<H", b[pos + 1:pos + 3])[0]
                vt = b[pos + 3]
                pos += 4
                if idx < len(self.subs):
                    vpos, vsz, _vt = self.subs[idx]
                    if t == 0x0E and _vt == 0x00:
                        continue
                    v, _ = self.value(vpos, _vt, vsz)
                    if (_vt & 0x7F) == 0x21:
                        out.append(v)
                    else:
                        out.append(_esc(v))
                continue
            break  # unknown token: stop, keep what we have
        return "".join(out)

    def _attr(self, pos, out, suppress):
        b = self.chunk
        noff = struct.unpack("<I", b[pos + 1:pos + 5])[0]
        pos += 5
        name = self.name(noff) or "?"
        parts = []
        while pos < len(b) and (b[pos] & 0x3F) in VALUE_TOKENS:
            t = b[pos] & 0x3F
            if t == 0x05:
                v, pos = self.value(pos + 2, b[pos + 1], -1)
            elif t in (0x0D, 0x0E):
                idx = struct.unpack("<H", b[pos + 1:pos + 3])[0]
                pos += 4
                if idx < len(self.subs):
                    vpos, vsz, vt = self.subs[idx]
                    v, _ = self.value(vpos, vt, vsz)
                else:
                    v = ""
            elif t == 0x08:
                v = "&#x%x;" % struct.unpack("<H", b[pos + 1:pos + 3])[0]
                pos += 3
            elif t == 0x09:
                noff2 = struct.unpack("<I", b[pos + 1:pos + 5])[0]
                v = "&" + (self.name(noff2) or "?") + ";"
                pos += 5
            else:  # cdata
                n = struct.unpack("<I", b[pos + 1:pos + 5])[0]
                v = b[pos + 5:pos + 5 + n].decode("utf-8", "replace")
                pos += 5 + n
            parts.append(v)
        if not suppress:
            out.append(" " + name + '="' + _esc("".join(parts)) + '"')
        return pos

    def _skip(self, pos, end):
        """consume one token inside a suppressed element."""
        b = self.chunk
        t = b[pos] & 0x3F
        if t in (0x02, 0x03, 0x04, 0x00):
            return pos + 1
        if t == 0x01:
            return pos + 11
        if t == 0x05:
            _, p2 = self.value(pos + 2, b[pos + 1], -1)
            return p2
        if t in (0x0D, 0x0E):
            return pos + 4
        if t in (0x07, 0x0B):
            n = struct.unpack("<I", b[pos + 1:pos + 5])[0]
            return pos + 5 + n
        if t == 0x0C:
            return self._instance(pos, [])
        return pos + 1

    def _instance(self, pos, out):
        """0x0C: 33-byte template-def header, fragment, instance data."""
        b = self.chunk
        t0 = pos + 1
        try:
            doff = struct.unpack("<I", b[t0 + 5:t0 + 9])[0]
            dsize = struct.unpack("<I", b[t0 + 29:t0 + 33])[0]
        except struct.error:
            return pos + 1
        hdr = t0 + 33
        frag_pos, frag_size, data_pos = None, 0, hdr
        if doff and doff != hdr and 0 < doff < len(b):
            # stored/shared def: bytes at doff may be another def header
            # or a raw fragment
            if b[doff] == 0x0F or (b[doff] & 0x3F) == 0x01:
                frag_pos, frag_size = doff, min(dsize or CHUNK,
                                                len(b) - doff)
            elif doff + 33 < len(b):
                frag_pos = doff + 33
                frag_size = struct.unpack("<I", b[doff + 29:doff + 33])[0]
        else:
            frag_pos, frag_size, data_pos = hdr, dsize, hdr + dsize
        # substitution values sit at data_pos
        count = struct.unpack("<I", b[data_pos:data_pos + 4])[0]
        desc = data_pos + 4
        subs, vpos = [], desc + count * 4
        for i in range(min(count, 4096)):
            vsz, vt = struct.unpack("<HB", b[desc + i * 4:desc + i * 4 + 3])
            subs.append((vpos, vsz, vt))
            vpos += vsz
        saved = self.subs
        self.subs = subs
        try:
            if frag_pos is not None:
                out.append(self.decode(frag_pos,
                                       min(frag_pos + frag_size, len(b))))
        finally:
            self.subs = saved
        return vpos


def _records(chunk):
    """yield (record_id, written_iso, binxml_offset) per valid record."""
    pos, end = 0x200, len(chunk)
    while pos + 24 <= end:
        i = chunk.find(REC_MAGIC, pos, end)
        if i < 0:
            return
        size = struct.unpack("<I", chunk[i + 4:i + 8])[0]
        if (24 <= size <= end - i
                and struct.unpack("<I", chunk[i + size - 4:i + size])[0]
                == size):
            rid = struct.unpack("<Q", chunk[i + 8:i + 16])[0]
            yield rid, _ft(chunk[i + 16:i + 24]), i + 24, i + size - 4
            pos = i + size
        else:
            pos = i + 4


def parse_evtx(path):
    """-> list of {record_id, written, xml} dicts."""
    data = Path(path).read_bytes()
    rows, errs = [], 0
    if not data.startswith(MAGIC):
        return rows, ["not an EVTX file (missing ElfFile magic)"]
    for coff in range(0x1000, len(data) - 8, CHUNK):
        chunk = data[coff:coff + CHUNK]
        if not chunk.startswith(CHUNK_MAGIC):
            continue
        dec = _Dec(chunk)
        for rid, written, boff, bend in _records(chunk):
            try:
                dec2 = _Dec(chunk)
                xml = dec2.decode(boff, bend)
            except Exception:
                errs += 1
                continue
            rows.append({"record_id": rid, "written": written,
                         "xml": xml})
    return rows, errs


def _selftest():
    """Build a one-record EVTX: template def + 3 substitutions."""
    names = ["Event", "System", "EventID", "TimeCreated", "EventData",
             "Data", "Name", "SystemTime"]
    chunk = bytearray(CHUNK)
    chunk[:8] = CHUNK_MAGIC
    noffs = {}
    sp = 0x3000
    for n in names:
        noffs[n] = sp
        e = n.encode("utf-16-le")
        struct.pack_into("<IHH", chunk, sp, 0, 0, len(n))
        chunk[sp + 8:sp + 8 + len(e)] = e
        sp += 8 + len(e) + 2
    frag = bytearray(b"\x0f\x01\x01\x00")

    def el(name, dep=0xFFFF, attrs=None, body=b""):
        hdr = bytes([0x41 if attrs else 0x01])
        hdr += struct.pack("<H", dep) + b"\x00" * 4
        hdr += struct.pack("<I", noffs[name])
        if attrs:
            ab = b""
            for an, av in attrs:
                e = av.encode("utf-16-le")
                ab += b"\x06" + struct.pack("<I", noffs[an])
                ab += b"\x05\x01" + struct.pack("<H", len(av)) + e
            hdr += struct.pack("<I", len(ab)) + ab
        return hdr + b"\x02" + body + b"\x04"

    def sub(idx, vt=0x01):
        return b"\x0d" + struct.pack("<HB", idx, vt)

    frag += el("Event", body=el("System", body=(
        el("EventID", body=sub(0, 0x07)) +
        el("TimeCreated", attrs=[("SystemTime", "x")], body=sub(1, 0x11))
    )) + el("EventData", body=el("Data", attrs=[("Name", "CommandLine")],
                                 body=sub(2, 0x01))))
    frag += b"\x00"
    inst = b"\x0c" + b"\x01" + struct.pack("<I", 1)
    def_pos = 0x200 + 24 + 4 + 1 + 33  # where def header sits in chunk
    inst += struct.pack("<I", def_pos) + struct.pack("<I", 0)
    inst += b"\x00" * 16 + struct.pack("<I", len(frag)) + frag
    vals = [struct.pack("<i", 4624),
            struct.pack("<Q", 133000000000000000),
            "flag{evtx_decode}".encode("utf-16-le")]
    inst += struct.pack("<I", 3)
    inst += b"".join(struct.pack("<HBB", len(v), t, 0)
                     for v, t in zip(vals, [0x07, 0x11, 0x01]))
    inst += b"".join(vals)
    rec = struct.pack("<Q", 7) + struct.pack("<Q", 133000000000000000)
    rec += b"\x0f\x01\x01\x00" + inst + b"\x00"
    rsize = 8 + len(rec) + 4
    chunk[0x200:0x200 + 8] = REC_MAGIC + struct.pack("<I", rsize)
    chunk[0x208:0x208 + len(rec)] = rec
    chunk[0x200 + rsize - 4:0x200 + rsize] = struct.pack("<I", rsize)
    data = MAGIC + b"\x00" * (0x1000 - 8) + bytes(chunk)
    tmp = Path(tempfile.mkdtemp()) / "t.evtx"
    tmp.write_bytes(data)
    rows, errs = parse_evtx(tmp)
    assert len(rows) == 1, (rows, errs)
    xml = rows[0]["xml"]
    assert "<EventID>4624</EventID>" in xml, xml
    assert "flag{evtx_decode}" in xml, xml
    assert 'Name="CommandLine"' in xml, xml
    print("evtx_parse selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="decode .evtx records to XML (stdlib BinXML)")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--strings", action="store_true",
                    help="also print UTF-16LE strings per record")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    rows, errs = parse_evtx(a.file)
    for r in rows:
        print(r["xml"])
        if a.strings:
            raw = r["xml"].encode("utf-8", "ignore")
            import re
            for s in re.findall(rb"[\x20-\x7e]{6,}", raw):
                print("  #", s.decode())
    print(json.dumps({"records": len(rows), "errors": errs}),
          file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
