#!/usr/bin/env python3
"""leveldb_dump.py -- LevelDB .log and .ldb/.sst reader.

Chrome/Chromium IndexedDB, and many CTF "database dump" handouts, are
LevelDB stores. `leveldb` the module is not installed here; the two
on-disk formats are documented and small enough to read directly.

  .log       32KiB blocks of physical records (crc/len/type); each
             logical record is a WriteBatch: seq(8) + count(4) +
             count * [tag|key|value]. Deletions are listed, not skipped.
  .ldb/.sst  block table: a 48-byte footer points at the index block;
             each data block is a restart-array of internal-key entries,
             compression flag 1 = raw snappy (implemented inline --
             the `snappy` module is absent).

  python3 tools/forensics/leveldb_dump.py 000003.log
  python3 tools/forensics/leveldb_dump.py 000005.ldb
  python3 tools/forensics/leveldb_dump.py --selftest
"""
import argparse
import json
import re
import struct
import sys


def _varint(b, i):
    v = s = 0
    while True:
        x = b[i]
        i += 1
        v |= (x & 0x7F) << s
        if not x & 0x80:
            return v, i
        s += 7


def snappy_decompress(b):
    """Raw snappy block (the format .ldb blocks use)."""
    total, i = _varint(b, 0)
    out = bytearray()
    while i < len(b):
        tag = b[i]
        i += 1
        typ = tag & 3
        if typ == 0:                                # literal
            n = tag >> 2
            if n < 60:
                n += 1
            else:
                nbytes = n - 59
                n = int.from_bytes(b[i:i + nbytes], "little") + 1
                i += nbytes
            out += b[i:i + n]
            i += n
        else:
            if typ == 1:
                n = ((tag >> 2) & 7) + 4
                off = ((tag >> 5) << 8) | b[i]
                i += 1
            elif typ == 2:
                n = (tag >> 2) + 1
                off = struct.unpack("<H", b[i:i + 2])[0]
                i += 2
            else:
                n = (tag >> 2) + 1
                off = struct.unpack("<I", b[i:i + 4])[0]
                i += 4
            for _ in range(n):
                out.append(out[-off])
    if len(out) != total:
        raise ValueError("snappy length %d != %d" % (len(out), total))
    return bytes(out)


# ---- .log ------------------------------------------------------------------

def parse_log(data):
    recs, i = [], 0
    while i + 7 <= len(data):
        blk = data[i:i + 32768]
        j = 0
        logical = b""
        while j + 7 <= len(blk):
            _crc, n, typ = struct.unpack("<IHB", blk[j:j + 7])
            j += 7
            if typ == 0 and n == 0:
                j = len(blk)
                break
            frag = blk[j:j + n]
            j += n
            if typ == 1:
                logical = frag
                recs.append(logical)
            elif typ == 2:
                logical = frag
            elif typ == 3:
                logical += frag
            elif typ == 4:
                logical += frag
                recs.append(logical)
        i += 32768
    out = {"format": "leveldb_log", "batches": []}
    for rec in recs:
        if len(rec) < 12:
            out["batches"].append({"error": "short writebatch",
                                   "size": len(rec)})
            continue
        seq, count = struct.unpack("<QI", rec[:12])
        p, entries = 12, []
        try:
            for _ in range(count):
                tag = rec[p]
                p += 1
                klen, p = _varint(rec, p)
                key = rec[p:p + klen]
                p += klen
                if tag == 1:
                    vlen, p = _varint(rec, p)
                    val = rec[p:p + vlen]
                    p += vlen
                    entries.append({"op": "put", "key": _show(key),
                                    "value": _show(val)})
                else:
                    entries.append({"op": "del", "key": _show(key)})
        except (IndexError, struct.error):
            entries.append({"error": "batch truncated at %d" % p})
        out["batches"].append({"seq": seq, "entries": entries})
    return out


def _show(b):
    try:
        t = b.decode("utf-8")
        if all(c.isprintable() for c in t):
            return t
    except UnicodeDecodeError:
        pass
    return "0x" + b.hex()


# ---- .ldb / .sst -----------------------------------------------------------

def _block(data, off, size):
    raw = data[off:off + size]
    ctype = data[off + size]
    if ctype == 0:
        return raw
    if ctype == 1:
        return snappy_decompress(raw)
    raise ValueError("unknown block compression %d" % ctype)


def _entries(block):
    out = []
    nrestarts = struct.unpack("<I", block[-4:])[0]
    end = len(block) - 4 - 4 * nrestarts
    p = 0
    last = b""
    while p < end:
        shared, p = _varint(block, p)
        non, p = _varint(block, p)
        vlen, p = _varint(block, p)
        key = last[:shared] + block[p:p + non]
        p += non
        val = block[p:p + vlen]
        p += vlen
        last = key
        out.append((key, val))
    return out


def parse_table(data):
    if len(data) < 48:
        return {"error": "too small for a table file"}
    foot = data[-48:]
    magic = struct.unpack("<Q", foot[40:48])[0]
    if magic != 0xDB4775248B80FB57:
        return {"error": "bad table magic 0x%x" % magic}
    _meta_off, _p = _varint(foot, 0)
    _meta_sz, _p = _varint(foot, _p)
    idx_off, _p2 = _varint(foot, _p)
    idx_sz, _p2 = _varint(foot, _p2)
    idx = _entries(_block(data, idx_off, idx_sz))
    out = {"format": "leveldb_table", "entries": []}
    for _ikey, handle in idx:
        d_off, p = _varint(handle, 0)
        d_sz, p = _varint(handle, p)
        for key, val in _entries(_block(data, d_off, d_sz)):
            ukey = key[:-8] if len(key) > 8 else key
            out["entries"].append({"key": _show(ukey),
                                   "value": _show(val)})
    return out


def analyze(data):
    if data[-48:-40] == struct.pack("<Q", 0xDB4775248B80FB57):
        return parse_table(data)
    return parse_log(data)


def _selftest():
    # --- .log ---
    batch = struct.pack("<QI", 1, 2)
    for k, v in ((b"_META\x01flag", b"flag{leveldb_log}"),
                 (b"k2", b"v2")):
        kb, vb = bytes([len(k)]) + k, bytes([len(v)]) + v
        batch += b"\x01" + kb + vb
    phys = struct.pack("<IHB", 0, len(batch), 1) + batch
    r = parse_log(phys + b"\x00" * 7)
    ent = r["batches"][0]["entries"]
    assert ent[0]["value"] == "flag{leveldb_log}", ent
    # --- .ldb ---
    def mkblock(pairs):
        body = b""
        for k, v in pairs:
            body += b"\x00" + bytes([len(k)]) + bytes([len(v)]) + k + v
        return body + struct.pack("<I", 0) + struct.pack("<I", 1)
    dblk = mkblock([(b"user\x01" + b"\x00" * 8, b"flag{in_sst}")])
    doff = 0
    idx_body = b""
    ikey = b"i1" + b"\x00" * 8
    handle = bytes([doff]) + bytes([len(dblk)])
    idx_body += b"\x00" + bytes([len(ikey)]) + bytes(
        [len(handle)]) + ikey + handle
    iblk = idx_body + struct.pack("<I", 0) + struct.pack("<I", 1)
    ioff = len(dblk) + 5
    foot = b"\x00\x00" + bytes([ioff]) + bytes([len(iblk)])
    foot = foot.ljust(40, b"\x00") + struct.pack("<Q", 0xDB4775248B80FB57)
    tbl = dblk + b"\x00" + b"\x00" * 4 + iblk + b"\x00" + b"\x00" * 4 + foot
    rt = parse_table(tbl)
    assert rt["entries"][0]["value"] == "flag{in_sst}", rt
    # snappy literal round trip
    lit = bytes([len(b"abcabc")]) + bytes([(3 - 1) << 2]) + b"abc" + \
        bytes([(3 - 1) << 2 | 2]) + struct.pack("<H", 3)
    assert snappy_decompress(lit) == b"abcabc"
    print("leveldb_dump selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="LevelDB .log/.ldb reader")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    print(json.dumps(analyze(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
