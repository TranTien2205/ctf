#!/usr/bin/env python3
"""Extract LSB-hidden data from PNG and BMP without zsteg/stegsolve.

The skill defers bit-plane work to external tools; none of them exist on
a bare box. This one does the whole job with stdlib: PNG IHDR/IDAT ->
zlib -> unfilter (all five filter types), BMP header + pixel array. It
then walks the zsteg-equivalent matrix — bit planes 1-3, channel sets
r/g/b/rgb/bgr/alpha, row and column order, lsb- and msb-first packing —
and reports any extraction whose bytes decode to printable text, with
the flag-format pass on top.

Bounded: images capped at 8M pixels, output capped at 1 MiB per stream,
8-bit channels only (16-bit and interlaced PNG reported as unsupported
rather than misread).

  python3 tools/forensics/lsb_scan.py img.png
  python3 tools/forensics/lsb_scan.py img.bmp --planes 1
  python3 tools/forensics/lsb_scan.py --selftest
"""
import argparse, json, os, re, struct, sys, zlib

_MAXPX = 8_000_000
_MAXOUT = 1 << 20
_FLAG = re.compile(rb"[A-Za-z0-9_]{2,16}\{[^\x00-\x1f}]{4,120}\}")


def paeth(a, b, c):
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else b if pb <= pc else c


def png_pixels(path):
    raw = open(path, "rb").read()
    if not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        return None, "not a PNG"
    off, idat, ihdr, plte = 8, b"", None, None
    while off + 8 <= len(raw):
        ln, typ = struct.unpack(">I4s", raw[off:off + 8])
        data = raw[off + 8:off + 8 + ln]
        off += 12 + ln
        if typ == b"IHDR":
            ihdr = struct.unpack(">IIBBBBB", data)
        elif typ == b"PLTE":
            plte = data
        elif typ == b"IDAT":
            idat += data
        elif typ == b"IEND":
            break
    if not ihdr or not idat:
        return None, "no IHDR/IDAT"
    w, h, depth, ctype, _c, _f, interlace = ihdr
    if w * h > _MAXPX:
        return None, "image over pixel cap"
    if interlace:
        return None, "interlaced PNG unsupported"
    if depth != 8:
        return None, "bit depth %d unsupported" % depth
    ch = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(ctype)
    if not ch:
        return None, "color type %d unsupported" % ctype
    try:
        dec = zlib.decompress(idat)
    except zlib.error as e:
        return None, "IDAT inflate: %s" % e
    stride, out, prev = w * ch, bytearray(), bytearray(w * ch)
    pos = 0
    for _y in range(h):
        f = dec[pos]
        pos += 1
        line = bytearray(dec[pos:pos + stride])
        pos += stride
        for i in range(stride):
            a_ = line[i - ch] if i >= ch else 0
            b_ = prev[i]
            c_ = prev[i - ch] if i >= ch else 0
            if f == 1:
                line[i] = (line[i] + a_) & 0xFF
            elif f == 2:
                line[i] = (line[i] + b_) & 0xFF
            elif f == 3:
                line[i] = (line[i] + (a_ + b_) // 2) & 0xFF
            elif f == 4:
                line[i] = (line[i] + paeth(a_, b_, c_)) & 0xFF
        out += line
        prev = line
    # normalise to RGBA tuples
    px = []
    if ctype == 3:
        if not plte:
            return None, "palette image without PLTE"
        px = [(plte[i * 3], plte[i * 3 + 1], plte[i * 3 + 2], 255)
              for i in out]
    elif ctype == 0:
        px = [(v, v, v, 255) for v in out]
    elif ctype == 4:
        px = [(out[i], out[i], out[i], out[i + 1])
              for i in range(0, len(out), 2)]
    elif ctype == 2:
        px = [(out[i], out[i + 1], out[i + 2], 255)
              for i in range(0, len(out), 3)]
    else:
        px = [(out[i], out[i + 1], out[i + 2], out[i + 3])
              for i in range(0, len(out), 4)]
    return (w, h, px), None


def bmp_pixels(path):
    raw = open(path, "rb").read()
    if not raw.startswith(b"BM") or len(raw) < 54:
        return None, "not a BMP"
    off = struct.unpack("<I", raw[10:14])[0]
    w = struct.unpack("<i", raw[18:22])[0]
    h = struct.unpack("<i", raw[22:26])[0]
    bpp = struct.unpack("<H", raw[28:30])[0]
    comp = struct.unpack("<I", raw[30:34])[0]
    if comp != 0 or bpp not in (24, 32) or w * abs(h) > _MAXPX:
        return None, "unsupported BMP (bpp=%s comp=%s)" % (bpp, comp)
    w_, h_, px = abs(w), abs(h), []
    stride = (w_ * bpp // 8 + 3) & ~3
    for y in range(h_):
        row = (h_ - 1 - y) if h > 0 else y
        base = off + row * stride
        for x in range(w_):
            p = base + x * (bpp // 8)
            b, g, r = raw[p], raw[p + 1], raw[p + 2]
            a = raw[p + 3] if bpp == 32 else 255
            px.append((r, g, b, a))
    return (w_, h_, px), None


_CH = {"r": 0, "g": 1, "b": 2, "a": 3,
       "rgb": (0, 1, 2), "bgr": (2, 1, 0), "rgba": (0, 1, 2, 3)}


def extract(px, w, h, chan, plane, order, msb):
    idx = _CH[chan]
    idx = (idx,) if isinstance(idx, int) else idx
    bits = []
    if order == "xy":
        seq = px
    else:
        seq = (px[x * h + y] for x in range(w) for y in range(h))
    for p in seq:
        for c in idx:
            bits.append((p[c] >> (plane - 1)) & 1)
            if len(bits) >= _MAXOUT * 8:
                break
        if len(bits) >= _MAXOUT * 8:
            break
    out = bytearray()
    for i in range(0, len(bits) - 7, 8):
        chunk = bits[i:i + 8]
        v = 0
        for j, b in enumerate(chunk):
            v |= b << ((7 - j) if msb else j)
        out.append(v)
    return bytes(out)


def printable_ratio(bs):
    if not bs:
        return 0.0
    good = sum(32 <= b < 127 or b in (9, 10, 13) for b in bs[:4096])
    return good / min(len(bs), 4096)


def scan(path, planes=(1, 2, 3)):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".png":
        got, err = png_pixels(path)
    elif ext == ".bmp":
        got, err = bmp_pixels(path)
    else:
        return None, "unsupported extension %s" % ext
    if err:
        return None, err
    w, h, px = got
    hits = []
    for plane in planes:
        for chan in ("r", "g", "b", "a", "rgb", "bgr"):
            for order in ("xy", "yx"):
                for msb in (False, True):
                    tag = "b%d,%s,%s,%s" % (
                        plane, chan, order, "msb" if msb else "lsb")
                    data = extract(px, w, h, chan, plane, order, msb)
                    flag = _FLAG.search(data)
                    if flag or printable_ratio(data[:512]) > 0.9:
                        head = data[:160].split(b"\x00")[0]
                        hits.append({
                            "stream": tag,
                            "printable": round(printable_ratio(data), 3),
                            "flag": flag.group(0).decode("utf-8", "replace")
                            if flag else None,
                            "head": head.decode("utf-8", "replace")[:120],
                        })
    return {"size": [w, h], "hits": hits,
            "note": "no hits: try --planes deeper or the carrier is not LSB"
            if not hits else "verify the flag against the challenge format"}, None


def _selftest() -> int:
    """Build a PNG with a flag hidden in b1 of the red channel."""
    import tempfile
    pt = b"flag{lsb_w0rks!!}\x00" + b"\x00" * 40
    w, h = 20, 24
    bits = []
    for byte in pt:
        bits += [(byte >> j) & 1 for j in range(8)]  # lsb-first
    px = [[80, 90, 100, 255] for _ in range(w * h)]
    for i, b in enumerate(bits):
        px[i][0] = (px[i][0] & ~1) | b
    raw = bytearray()
    for y in range(h):
        raw.append(0)
        for x in range(w):
            r, g, b_, _a = px[y * w + x]
            raw += bytes((r, g, b_))

    def chunk(typ, data):
        return (struct.pack(">I", len(data)) + typ + data
                + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(bytes(raw)))
           + chunk(b"IEND", b""))
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(png)
        path = f.name
    try:
        out, err = scan(path, planes=(1,))
        assert err is None, err
        streams = [h_["stream"] for h_ in out["hits"]]
        assert any(h_["flag"] and "lsb_w0rks" in h_["flag"]
                   for h_ in out["hits"]), out
        assert "b1,r,xy,lsb" in streams, streams
    finally:
        os.unlink(path)
    print("lsb_scan selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("image", nargs="?")
    ap.add_argument("--planes", default="1,2,3")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.image:
        ap.error("image path is required")
    planes = tuple(int(p) for p in a.planes.split(",") if p.strip())
    out, err = scan(a.image, planes)
    if err:
        print(json.dumps({"error": err}))
        return 1
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
