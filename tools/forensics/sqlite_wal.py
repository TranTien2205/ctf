#!/usr/bin/env python3
"""sqlite_wal.py -- read a SQLite -wal file before it checkpoints away.

Rows deleted or overwritten between commits live only in the -wal
file; opening the db with sqlite3 replays (checkpoints) the WAL and
destroys the evidence. This parses the 32-byte WAL header and each
24-byte frame header + page image directly, lists every committed
frame with its page number, and scans each page image for printable
runs — enough to spot a flag written then deleted pre-checkpoint.

  python3 tools/forensics/sqlite_wal.py db-wal frames
  python3 tools/forensics/sqlite_wal.py db-wal strings
  python3 tools/forensics/sqlite_wal.py db-wal page 7
  python3 tools/forensics/sqlite_wal.py --selftest

`page N` writes the newest image of page N to stdout. strings mode
attributes every hit to the frame whose image contained it, so a
value present in frame 2 but gone by frame 5 reads as 'deleted in
frame 5'. Salt mismatches (post-checkpoint stale frames) are marked
stale, not trusted.
"""
import argparse
import json
import re
import struct
import sys


def parse(data):
    if len(data) < 32:
        return {"error": "truncated wal header"}
    magic, _fmt, psize, seq, s1, s2, _c1, _c2 = struct.unpack(
        ">8I", data[0:32])
    if magic not in (0x377F0682, 0x377F0683):
        return {"error": f"bad wal magic 0x{magic:08x}"}
    hdr = {"page_size": psize, "ckpt_seq": seq,
           "salt1": hex(s1), "salt2": hex(s2)}
    frames, off, n = [], 32, 0
    while off + 24 + psize <= len(data):
        pg, dbsz, fs1, fs2 = struct.unpack(">4I", data[off:off + 16])
        stale = (fs1, fs2) != (s1, s2)
        n += 1
        frames.append({
            "frame": n, "page": pg, "offset": off + 24,
            "db_pages_after_commit": dbsz, "commit": bool(dbsz),
            "stale": stale})
        off += 24 + psize
    return {"header": hdr, "frames": frames, "psize": psize,
            "trailing": len(data) - off}


def strings(data, min_len=6):
    p = parse(data)
    if "error" in p:
        return p
    psize = p["psize"]
    out = []
    for f in p["frames"]:
        img = data[f["offset"]:f["offset"] + psize]
        for m in re.finditer(rb"[ -~]{%d,}" % min_len, img):
            out.append({"frame": f["frame"], "page": f["page"],
                        "offset_in_page": m.start(),
                        "stale": f["stale"],
                        "string": m.group().decode("ascii", "replace")})
    return {"header": p["header"], "hits": out}


def _selftest():
    psize = 512
    def frame(pg, dbsz, s1, s2, payload):
        return (struct.pack(">4I", pg, dbsz, s1, s2)
                + b"\x00" * 8 + payload.ljust(psize, b"\x00"))
    wal = struct.pack(">8I", 0x377F0682, 3007000, psize, 0,
                      0xAA, 0xBB, 0, 0)
    wal += frame(2, 0, 0xAA, 0xBB, b"flag{wal_not_yet_checkpointed}")
    wal += frame(2, 3, 0xAA, 0xBB, b"\x00" * 64)   # commit, page rewritten
    wal += frame(4, 4, 0xCC, 0xDD, b"stale-frame-junk")
    p = parse(wal)
    assert len(p["frames"]) == 3 and p["frames"][2]["stale"], p
    s = strings(wal)
    flag_hit = [h for h in s["hits"] if "flag{" in h["string"]]
    assert flag_hit and flag_hit[0]["frame"] == 1, flag_hit
    assert not any("stale-frame" in h["string"]
                   and not h["stale"] for h in s["hits"])
    print("sqlite_wal selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="SQLite WAL reader")
    ap.add_argument("wal", nargs="?")
    ap.add_argument("cmd", nargs="?",
                    choices=["frames", "strings", "page"])
    ap.add_argument("page", nargs="?", type=int)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not (a.wal and a.cmd):
        ap.error("wal path and cmd required")
    data = open(a.wal, "rb").read()
    if a.cmd == "strings":
        print(json.dumps(strings(data), indent=1))
        return
    p = parse(data)
    if a.cmd == "frames":
        print(json.dumps(p, indent=1))
        return
    if "error" in p:
        sys.exit(p["error"])
    if a.page is None:
        ap.error("page needs a page number")
    newest = None
    for f in p["frames"]:
        if f["page"] == a.page and not f["stale"]:
            newest = f
    if newest is None:
        sys.exit(f"no live frame for page {a.page}")
    sys.stdout.buffer.write(
        data[newest["offset"]:newest["offset"] + p["psize"]])


if __name__ == "__main__":
    raise SystemExit(main())
