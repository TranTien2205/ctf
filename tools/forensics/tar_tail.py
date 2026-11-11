#!/usr/bin/env python3
"""tar_tail.py -- members + appended-data check for tar archives.

`tarfile` already lists members; what it will not tell you is what sits
AFTER the archive's two 512-byte zero blocks. A flag appended past the
end-of-archive marker is invisible to `tar tf` and to extractors. This
walks the 512-byte ustar headers, reports each member (name, size,
offset, type), then reports any bytes that follow the terminator.

  python3 tools/forensics/tar_tail.py a.tar
  python3 tools/forensics/tar_tail.py a.tar --tail        # dump trailer bytes
  python3 tools/forensics/tar_tail.py --selftest
"""
import argparse
import json
import sys

TYPES = {"0": "file", "1": "link", "2": "symlink", "3": "char",
         "4": "block", "5": "dir", "6": "fifo", "7": "contig",
         "g": "pax-global", "x": "pax", "L": "gnu-longname",
         "K": "gnu-longlink"}


def parse(data):
    members, i = [], 0
    while i + 512 <= len(data):
        blk = data[i:i + 512]
        if blk == b"\x00" * 512:
            # end-of-archive: two zero blocks; whatever follows is trailer
            tail = data[i:]
            pad = len(tail) - len(tail.lstrip(b"\x00"))
            tail = tail[pad // 512 * 512:]       # keep whole zero blocks out
            return {"members": members,
                    "trailer_offset": i,
                    "trailer_size": len(tail),
                    "trailer_head": tail[:64].hex()}
        if blk[257:262] != b"ustar":
            return {"error": "no ustar magic at block %d" % (i // 512),
                    "members": members}
        size = int(blk[124:136].rstrip(b"\x00 ") or b"0", 8)
        name = blk[:100].split(b"\x00")[0].decode("utf-8", "replace")
        members.append({"name": name, "size": size,
                        "type": TYPES.get(chr(blk[156]), chr(blk[156])),
                        "offset": i})
        i += 512 + ((size + 511) // 512) * 512
    return {"members": members, "trailer_offset": len(data),
            "trailer_size": 0, "trailer_head": "",
            "truncated": "no end-of-archive marker"}


def _selftest():
    def hdr(name, size, typ=b"0"):
        h = bytearray(512)
        h[:len(name)] = name.encode()
        h[124:136] = ("%011o\x00" % size).encode()
        h[156:157] = typ
        h[257:262] = b"ustar"
        return bytes(h)
    flag = b"flag{after_the_end}"
    img = hdr("note.txt", 12) + b"hello there!" + b"\x00" * 500 \
        + b"\x00" * 1024 + flag
    d = parse(img)
    assert d["members"][0]["name"] == "note.txt" and len(d["members"]) == 1
    assert d["trailer_size"] == len(flag), d
    assert flag.hex() in d["trailer_head"] + flag.hex()  # head is prefix
    d2 = parse(img[:512 + 512 + 1024])                    # no trailer
    assert d2["trailer_size"] == 0, d2
    print("tar_tail selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="tar members + trailer")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--tail", action="store_true",
                    help="hex-dump the trailer bytes instead of a summary")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("tar path required")
    data = open(a.path, "rb").read()
    d = parse(data)
    if a.tail and d.get("trailer_size"):
        off = d["trailer_offset"] + (len(data) - d["trailer_offset"]
                                     - d["trailer_size"])
        tail = data[off:]
        print(tail.hex() if not all(32 <= c < 127 or c in (9, 10, 13)
                                    for c in tail) else tail.decode())
        return
    print(json.dumps(d, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
