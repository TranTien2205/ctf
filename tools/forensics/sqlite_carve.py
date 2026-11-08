#!/usr/bin/env python3
"""sqlite_carve.py -- deleted-row recovery for SQLite database files.

Usage:
  python3 tools/forensics/sqlite_carve.py FILE          # carved rows, JSON
  python3 tools/forensics/sqlite_carve.py FILE --live   # include live cells
  python3 tools/forensics/sqlite_carve.py --selftest

A DELETE (or DROP TABLE) without VACUUM leaves cell bytes behind in
three places: the page's freeblock chain, the unallocated gap between
the cell-pointer array and the cell content area, and whole pages on
the freelist. This walks all three and re-decodes whatever record
structures are still intact: varint payload size + rowid + serial-type
header + column values.

What it does NOT do: decode index cells (0x0A) or records spilled to
overflow pages (payload > usable-35 shows as truncated). Rollback-
journal / -wal sidecars are separate files; carve them by passing the
journal file itself -- cells are not page-aligned there so the scan
degrades to a raw sweep, which still finds full records.

For serial-type byte-diff forensics (RITSEC-style two-file diff) use
`strings`/xxd on the record offsets this tool prints.
"""
import json
import sqlite3
import struct
import sys
import tempfile
from pathlib import Path

MAGIC = b"SQLite format 3\x00"
INT_SZ = {1: 1, 2: 2, 3: 3, 4: 4, 5: 6, 6: 8}
PACKERS = {2: "H", 4: "I", 8: "Q"}


def _varint(buf, off):
    v = 0
    for i in range(9):
        if off + i >= len(buf):
            return None, 0
        b = buf[off + i]
        if i == 8:
            return ((v << 8) | b), 9
        v = (v << 7) | (b & 0x7F)
        if not (b & 0x80):
            return v, i + 1
    return None, 0


def _colsize(t):
    if t in INT_SZ:
        return INT_SZ[t]
    if t in (0, 8, 9):
        return 0
    if t == 7:
        return 8
    if t >= 12:
        return (t - 12) // 2 if t % 2 == 0 else (t - 13) // 2
    return None  # 10, 11 reserved


def _decode(buf, off, t):
    sz = _colsize(t)
    if sz is None or off + sz > len(buf):
        return None, sz or 0
    raw = buf[off:off + sz]
    if t == 0:
        return None, 0
    if t in INT_SZ:
        return int.from_bytes(raw, "big", signed=True), sz
    if t == 7:
        return struct.unpack(">d", raw)[0], sz
    if t == 8:
        return 0, 0
    if t == 9:
        return 1, 0
    if t >= 12 and t % 2 == 0:
        return {"blob": raw.hex()}, sz
    try:
        return raw.decode("utf-8"), sz
    except UnicodeDecodeError:
        return {"blob": raw.hex()}, sz


def _record(buf, off, plen):
    """decode a record of plen bytes starting at off.
    returns (values list, types) or None."""
    hlen, hn = _varint(buf, off)
    if hlen is None or hlen < hn or hlen > plen or off + hlen > len(buf):
        return None
    types = []
    p = off + hn
    while p < off + hlen:
        t, n = _varint(buf, p)
        if t is None or n == 0 or t in (10, 11):
            return None
        types.append(t)
        p += n
    if p != off + hlen or not types or len(types) > 64:
        return None
    vals, q = [], off + hlen
    if q + sum(_colsize(t) or 0 for t in types) > off + plen:
        return None
    for t in types:
        v, sz = _decode(buf, q, t)
        if sz is None or q + sz > off + plen:
            return None
        vals.append(v)
        q += sz
    return vals, types, q - off


def _cell(buf, off, usable):
    """try a leaf-table cell at buf[off]: psize varint, rowid, record."""
    psize, n1 = _varint(buf, off)
    if psize is None or psize < 2 or psize > usable:
        return None
    rowid, n2 = _varint(buf, off + n1)
    if rowid is None or n2 == 0:
        return None
    rec = _record(buf, off + n1 + n2, psize)
    if not rec:
        return None
    return {"rowid": rowid, "values": rec[0], "types": rec[1]}


def _raw_record(buf, off, plen):
    """record without the cell wrapper -- the shape left in a
    freeblock after its 4-byte next/size header clobbers the
    psize+rowid varints of the freed cell."""
    rec = _record(buf, off, plen)
    if not rec:
        return None
    return {"values": rec[0], "types": rec[1], "consumed": rec[2]}


def _tail_record(buf, off, plen):
    """the tail of a record whose header was clobbered: serial types
    followed by values, ending exactly at off+plen. A freed cell's
    first 4 bytes (psize/rowid varints, hlen, first type) get
    overwritten by the freeblock header, so what survives starts
    mid-record -- recover it by trying k leading serial types whose
    values land flush on the region end."""
    for k in range(1, min(25, plen + 1)):
        types = []
        ok = True
        for i in range(k):
            if off + i >= len(buf):
                ok = False
                break
            t = buf[off + i]
            if t in (10, 11) or t & 0x80:
                ok = False
                break
            types.append(t)
        if not ok:
            continue
        need = sum(_colsize(t) for t in types)
        if off + k + need == off + plen:
            vals, q = [], off + k
            for t in types:
                v, sz = _decode(buf, q, t)
                if sz is None:
                    ok = False
                    break
                vals.append(v)
                q += sz
            if ok:
                return {"values": vals, "types": types,
                        "consumed": k + need, "tail": True}
    return None


def _quality(row):
    for v in row["values"]:
        if isinstance(v, str) and len(v) >= 3:
            printable = sum(c.isprintable() for c in v)
            if printable / len(v) >= 0.7:
                return "strong"
    return "weak"


def _regions(data, psize, npage, freelist_head, reserved):
    """yield (page_no, kind, start, end) byte ranges worth scanning."""
    for pg in range(1, npage + 1):
        base = (pg - 1) * psize
        page = data[base:base + psize]
        hoff = 100 if pg == 1 else 0
        if len(page) <= hoff + 8:
            continue
        ptype = page[hoff]
        if ptype == 0x0D:  # leaf table page
            fb = struct.unpack(">H", page[hoff + 1:hoff + 3])[0]
            ncell = struct.unpack(">H", page[hoff + 3:hoff + 5])[0]
            cstart = struct.unpack(">H", page[hoff + 5:hoff + 7])[0] or psize
            gap_start = hoff + 8 + ncell * 2
            if gap_start < cstart <= psize:
                yield pg, "unallocated", base + gap_start, base + cstart
            seen = set()
            while fb and fb not in seen and fb + 4 <= psize:
                seen.add(fb)
                nxt, sz = struct.unpack(">HH", page[fb:fb + 4])
                if sz >= 4 and fb + sz <= psize:
                    yield pg, "freeblock", base + fb, base + fb + sz
                fb = nxt
        elif ptype in (0x02, 0x05, 0x0A):
            continue  # interior pages / index leaves hold no rows
        else:
            # unparseable header -> maybe a stale free page; scan all
            yield pg, "raw", base, base + psize - reserved
    # explicit freelist trunk walk: the leaf pages it names are raw
    trunk = freelist_head
    seen = set()
    while trunk and trunk not in seen and 1 <= trunk <= npage:
        seen.add(trunk)
        base = (trunk - 1) * psize
        tp = data[base:base + psize]
        if len(tp) < 8:
            break
        nxt, nleaf = struct.unpack(">II", tp[:8])
        yield trunk, "trunk", base + 8 + nleaf * 4, base + psize - reserved
        for i in range(min(nleaf, (psize - 8) // 4)):
            ln = struct.unpack(">I", tp[8 + i * 4:12 + i * 4])[0]
            if 1 <= ln <= npage:
                lb = (ln - 1) * psize
                yield ln, "freelist", lb, lb + psize - reserved
        trunk = nxt


def carve(path, include_live=False):
    data = Path(path).read_bytes()
    if not data.startswith(MAGIC):
        return {"error": "not a SQLite file"}
    psize = struct.unpack(">H", data[16:18])[0]
    psize = 65536 if psize == 1 else psize
    reserved = data[20]
    freelist_head = struct.unpack(">I", data[32:36])[0]
    npage = len(data) // psize
    usable = psize - reserved - 35
    rows, live_offsets = [], set()
    # first pass: live cells (to tag and optionally emit)
    for pg in range(1, npage + 1):
        base = (pg - 1) * psize
        page = data[base:base + psize]
        hoff = 100 if pg == 1 else 0
        if len(page) <= hoff + 8 or page[hoff] != 0x0D:
            continue
        ncell = struct.unpack(">H", page[hoff + 3:hoff + 5])[0]
        for i in range(ncell):
            co = struct.unpack(
                ">H", page[hoff + 8 + i * 2:hoff + 10 + i * 2])[0]
            if not (hoff + 8 <= co < psize):
                continue
            live_offsets.add((pg, co))
            if include_live:
                r = _cell(page, co, usable)
                if r:
                    r.update(page=pg, offset=co, source="live")
                    rows.append(r)
    # second pass: carve the dead regions
    for pg, kind, s, e in _regions(data, psize, npage,
                                   freelist_head, reserved):
        page_base = (pg - 1) * psize
        off = s
        while off < e:
            rel = off - page_base
            if (pg, rel) in live_offsets:
                off += 1
                continue
            r = _cell(data, off, usable)
            if r:
                r.update(page=pg, offset=rel, source=kind,
                         quality=_quality(r))
                rows.append(r)
                off += 4
                continue
            r = _raw_record(data, off, e - off)
            if r and _quality(r) == "strong":
                r.update(page=pg, offset=rel, source=kind + "-record",
                         quality="strong")
                rows.append(r)
                off += r["consumed"]
                continue
            r = _tail_record(data, off, e - off)
            if r and _quality(r) == "strong":
                r.update(page=pg, offset=rel, source=kind + "-tail",
                         quality="strong")
                rows.append(r)
                off += r["consumed"]
            else:
                off += 1
    return {"file": str(path), "page_size": psize, "pages": npage,
            "rows": rows,
            "carved": sum(1 for r in rows if r.get("source") != "live")}


def _selftest():
    tmp = Path(tempfile.mkdtemp()) / "t.db"
    con = sqlite3.connect(tmp)
    con.execute("CREATE TABLE s(id INTEGER PRIMARY KEY, k TEXT, v TEXT)")
    con.executemany("INSERT INTO s(k,v) VALUES(?,?)", [
        ("noise", "aaaa" * 20),
        ("flag", "flag{deleted_row_forensics}"),
        ("noise2", "bbbb" * 20),
    ])
    con.commit()
    con.execute("DELETE FROM s WHERE k='flag'")
    con.commit()
    con.close()
    out = carve(tmp)
    hits = [r for r in out["rows"]
            if r["source"] != "live" and
            any("flag{deleted_row_forensics}" in str(v)
                for v in r["values"])]
    assert hits, out["rows"]
    # live pass must not tag the deleted row as live
    out2 = carve(tmp, include_live=True)
    assert any(r["source"] == "live" for r in out2["rows"])
    print("sqlite_carve selftest: ok")


def main():
    import argparse
    ap = argparse.ArgumentParser(
        description="carve deleted rows out of a SQLite file")
    ap.add_argument("file", nargs="?")
    ap.add_argument("--live", action="store_true",
                    help="also emit live leaf cells (source=live)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.file:
        ap.error("file required")
    print(json.dumps(carve(a.file, include_live=a.live), indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
