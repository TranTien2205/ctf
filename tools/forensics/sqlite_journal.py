#!/usr/bin/env python3
"""sqlite_journal.py -- SQLite rollback journal (db-journal) recovery.

A hot rollback journal holds the PRE-transaction image of every page
a write touched -- the file a deleted row lives in before the commit
overwrites it. sqlite_carve reads free space in the live database;
this reads the sibling `*.db-journal` that forensic bundles ship next
to it.

Format per the SQLite file spec: 28-byte header (magic
d9d505f920a163d7, record count, checksum nonce, db size, sector
size, page size -- all big-endian), then records of
pgno(4) + page + checksum(4). Multi-transaction journals are
"sections" each with their own header, sector-aligned. Table-leaf
pages (0x0D) get their cells decoded through sqlite_carve's parser;
non-leaf pages are still reported and hex-dumpable with --pages.

  python3 tools/forensics/sqlite_journal.py app.db-journal
  python3 tools/forensics/sqlite_journal.py app.db-journal --pages out/
  python3 tools/forensics/sqlite_journal.py --selftest
"""
import argparse
import json
import os
import struct

MAGIC = b"\xd9\xd5\x05\xf9\x20\xa1\x63\xd7"


def _rows(page):
    """Decode a table-leaf page's cells via sqlite_carve's parser."""
    try:
        from sqlite_carve import _cell
    except ImportError:
        import sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from sqlite_carve import _cell
    if len(page) < 8 or page[0] != 0x0D:
        return None
    ncells, = struct.unpack(">H", page[3:5])
    rows = []
    for i in range(min(ncells, 4096)):
        ptr, = struct.unpack(">H", page[8 + 2 * i:10 + 2 * i])
        if not 8 <= ptr < len(page):
            continue
        cell = _cell(page, ptr, len(page))
        if cell:
            rows.append(cell)
    return rows


def parse(data):
    out = {"sections": [], "records": [], "rows": []}
    pos = 0
    while pos + 28 <= len(data) and data[pos:pos + 8] == MAGIC:
        nrec, nonce, dbpages, sector, psize = struct.unpack(
            ">IIIII", data[pos + 8:pos + 28])
        if not psize or not (512 <= psize <= 65536):
            break
        nrec = 0x100000 if nrec == 0xFFFFFFFF else nrec
        sec = {"offset": pos, "db_pages": dbpages,
               "page_size": psize, "declared_records": nrec}
        rpos = pos + 28
        n = 0
        while n < nrec and rpos + 4 + psize + 4 <= len(data):
            pgno, = struct.unpack(">I", data[rpos:rpos + 4])
            page = data[rpos + 4:rpos + 4 + psize]
            cksum, = struct.unpack(">I", data[rpos + 4 + psize:
                                              rpos + 8 + psize])
            rec = {"section": len(out["sections"]), "pgno": pgno,
                   "offset": rpos, "checksum": cksum,
                   "type": {0x02: "index-interior", 0x05: "table-interior",
                            0x0A: "index-leaf", 0x0D: "table-leaf"}.get(
                            page[0], hex(page[0]))}
            rows = _rows(page)
            if rows:
                rec["rows"] = len(rows)
                for row in rows:
                    row["pgno"] = pgno
                    out["rows"].append(row)
            out["records"].append(rec)
            n += 1
            rpos += 4 + psize + 4
        sec["records"] = n
        out["sections"].append(sec)
        # next section starts at the next sector boundary
        sector = max(sector, 512)
        pos = ((rpos + sector - 1) // sector) * sector
        if pos < rpos + 8:          # avoid stalling on small sectors
            pos = rpos
    if not out["sections"]:
        return {"error": "no journal section (bad magic/size)"}
    return out


def _selftest():
    import tempfile
    psize = 512
    # leaf page with one cell: header 8B, cell ptr array, cell at tail
    page = bytearray(psize)
    page[0] = 0x0D
    struct.pack_into(">H", page, 3, 1)           # 1 cell
    payload = b"flag{journal_row}"
    plen = 2 + len(payload)
    cell_off = psize - 3 - plen
    struct.pack_into(">H", page, 8, cell_off)
    # cell: psize varint, rowid varint, record(hdr len, type 0x17? use
    # text type = 13+2*len odd -> 0x23 for len 17*2+13=47=0x2F)
    hdr_t = 13 + 2 * len(payload)
    rec = bytes([2, hdr_t]) + payload
    cell = bytes([plen, 7]) + rec
    page[cell_off:cell_off + len(cell)] = cell
    j = bytearray()
    j += MAGIC + struct.pack(">IIIII", 1, 0x1234, 2, 512, psize)
    j += struct.pack(">I", 2) + bytes(page) + struct.pack(">I", 0)
    out = parse(bytes(j))
    assert out["sections"][0]["records"] == 1
    assert out["records"][0]["pgno"] == 2
    rows = out["rows"]
    assert rows and rows[0]["values"] == [payload.decode()], rows
    assert rows[0]["rowid"] == 7
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "j")
        open(p, "wb").write(bytes(j))
        out2 = parse(open(p, "rb").read())
        assert out2["rows"] == rows
    assert parse(b"junk")["error"]
    print("sqlite_journal selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="SQLite rollback journal recovery")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--pages", help="dump recovered page images to dir")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    data = open(a.path, "rb").read()
    out = parse(data)
    if a.pages and "records" in out:
        os.makedirs(a.pages, exist_ok=True)
        psize = out["sections"][0]["page_size"] if out["sections"] \
            else 0
        for rec in out["records"]:
            page = data[rec["offset"] + 4:rec["offset"] + 4 + psize]
            open(os.path.join(
                a.pages, "page_%d.bin" % rec["pgno"]), "wb").write(page)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
