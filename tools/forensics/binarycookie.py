#!/usr/bin/env python3
"""binarycookie.py -- Safari Cookies.binarycookies inventory.

Safari stores cookies in ~/Library/Cookies/Cookies.binarycookies
(macOS and iOS images both show up in Sherlock-style bundles).
Format: "cook" magic, page count and page sizes big-endian, then
pages of 0x00000100-header + count + offset table. Each record
holds little-endian offsets to the url/name/path/value strings,
flags (1 secure, 4 httpOnly), and Mac-absolute-time expiry /
creation f64s (seconds since 2001-01-01). Session tokens show up
here -- this answers "what was in the user's browser session"
when the bundle ships Cookies.binarycookies.

  python3 tools/forensics/binarycookie.py Cookies.binarycookies
  python3 tools/forensics/binarycookie.py --selftest
"""
import argparse
import datetime
import json
import struct

MAGIC = b"cook"
MAC_EPOCH = 978307200          # 2001-01-01 in unix time


def _mt(v):
    try:
        return datetime.datetime.fromtimestamp(
            MAC_EPOCH + v, datetime.timezone.utc).replace(
            tzinfo=None).isoformat()
    except (OverflowError, OSError, ValueError):
        return "%r" % v


def _str(rec, off):
    if off <= 0 or off >= len(rec):
        return ""
    end = rec.find(b"\x00", off)
    if end < 0:
        end = len(rec)
    return rec[off:end].decode("utf-8", "replace")


def parse(data):
    if len(data) < 8 or data[:4] != MAGIC:
        return {"error": "not a binarycookies file"}
    npages, = struct.unpack(">I", data[4:8])
    sizes = struct.unpack(">%dI" % npages, data[8:8 + 4 * npages])
    cookies = []
    pos = 8 + 4 * npages
    for psz in sizes:
        page = data[pos:pos + psz]
        pos += psz
        if len(page) < 8 or page[:4] != b"\x00\x00\x01\x00":
            continue
        count, = struct.unpack(">I", page[4:8])
        for i in range(count):
            off, = struct.unpack(">I", page[8 + 4 * i:12 + 4 * i])
            if off + 56 > len(page):
                continue
            rec = page[off:]
            rsize, = struct.unpack("<I", rec[:4])
            flags, = struct.unpack("<I", rec[8:12])
            rec = rec[:rsize] if 8 <= rsize <= len(rec) else rec
            u_off, n_off, p_off, v_off = struct.unpack(
                "<IIII", rec[16:32])
            exp, crt = struct.unpack("<dd", rec[40:56])
            cookies.append({
                "url": _str(rec, u_off), "name": _str(rec, n_off),
                "path": _str(rec, p_off), "value": _str(rec, v_off),
                "secure": bool(flags & 1), "httponly": bool(flags & 4),
                "flags": flags, "expires": _mt(exp),
                "created": _mt(crt)})
    return {"pages": npages, "cookies": cookies}


def _mkrec(url, name, path, value, flags, exp):
    hdr = bytearray(56)
    strings = url + b"\x00" + name + b"\x00" + path + b"\x00" + \
        value + b"\x00"
    u, n, p, v = 56, 56 + len(url) + 1, \
        56 + len(url) + len(name) + 2, \
        56 + len(url) + len(name) + len(path) + 3
    struct.pack_into("<I", hdr, 8, flags)
    struct.pack_into("<IIII", hdr, 16, u, n, p, v)
    struct.pack_into("<dd", hdr, 40, exp, exp - 3600)
    rec = hdr + strings
    struct.pack_into("<I", rec, 0, len(rec))
    return bytes(rec)


def _selftest():
    recs = [
        _mkrec(b".ctf.local", b"session", b"/",
               b"flag{safari_cookie}", 5, 700000000.0),
        _mkrec(b"example.com", b"pref", b"/x", b"dark", 0,
               650000000.0)]
    offs = b"".join(struct.pack(">I", 8 + 4 * len(recs) + i * 0)
                    for i in range(0))          # placeholder, computed below
    base = 8 + 4 * len(recs)
    offs = b"".join(struct.pack(">I", base + sum(
        len(r) for r in recs[:i])) for i in range(len(recs)))
    page = b"\x00\x00\x01\x00" + struct.pack(">I", len(recs)) + \
        offs + b"".join(recs)
    data = MAGIC + struct.pack(">I", 1) + struct.pack(">I", len(page)) \
        + page
    out = parse(data)
    assert out["pages"] == 1 and len(out["cookies"]) == 2, out
    c = out["cookies"][0]
    assert c["url"] == ".ctf.local" and c["name"] == "session"
    assert c["value"] == "flag{safari_cookie}", c
    assert c["secure"] and c["httponly"]
    assert c["expires"].startswith("2023"), c["expires"]
    assert parse(b"short")["error"]
    print("binarycookie selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="Safari binarycookies")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("path required")
    print(json.dumps(parse(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
