#!/usr/bin/env python3
"""img_struct.py -- image container structure: chunks, markers, trailer.

The first look at a stego image is structural: what chunks exist,
whether data continues after the format's end-of-image marker, and
whether a second format signature (PK, Rar, pdf, png) is appended.
meta_read.py answers 'what does the metadata say'; this answers
'what else is in the file'.

  python3 tools/forensics/img_struct.py photo.png
  python3 tools/forensics/img_struct.py --selftest

PNG: chunk list with crc-valid flag; bytes after IEND reported as
trailer. JPEG: marker walk to SOS, then scan to EOI; trailer after
FFD9. GIF: trailer 0x3B; data after it. Other magic falls back to
ioc_scan-style signature offsets only.
"""
import argparse
import json
import struct
import sys
import zlib

EMBED = {b"PK\x03\x04": "zip", b"Rar!\x1a\x07": "rar",
         b"%PDF": "pdf", b"\x89PNG": "png", b"\xff\xd8\xff": "jpeg",
         b"GIF8": "gif", b"7z\xbc\xaf": "7z"}


def _embedded(data, skip_first=0):
    hits = []
    for sig, name in EMBED.items():
        i = skip_first
        while True:
            i = data.find(sig, i)
            if i < 0:
                break
            hits.append({"offset": i, "format": name})
            i += 1
    return sorted(hits, key=lambda h: h["offset"])


def png(data):
    out = {"format": "png"}
    chunks, off = [], 8
    while off + 12 <= len(data):
        size, typ = struct.unpack(">I4s", data[off:off + 8])
        typ = typ.decode("latin-1")
        crc_ok = None
        if off + 12 + size <= len(data):
            body = data[off + 4:off + 8 + size]
            crc = struct.unpack(">I",
                                data[off + 8 + size:off + 12 + size])[0]
            crc_ok = zlib.crc32(body) & 0xFFFFFFFF == crc
        chunks.append({"type": typ, "offset": off, "size": size,
                       "crc_ok": crc_ok})
        off += 12 + size
        if typ == "IEND":
            break
    out["chunks"] = chunks
    out["crc_bad"] = [c["type"] for c in chunks if c["crc_ok"] is False]
    out["trailer"] = len(data) - off if len(data) > off else 0
    if out["trailer"]:
        out["trailer_preview"] = data[off:off + 64].hex()
    return out, off


def jpeg(data):
    out = {"format": "jpeg"}
    markers, off = [], 2
    eoi = None
    while off + 1 < len(data):
        if data[off] != 0xFF:
            off += 1
            continue
        m = data[off + 1]
        if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7 or m == 0x01:
            markers.append({"marker": f"FF{m:02X}", "offset": off})
            if m == 0xD9:
                eoi = off + 2
                break
            off += 2
            continue
        if off + 4 > len(data):
            break
        sz = struct.unpack(">H", data[off + 2:off + 4])[0]
        markers.append({"marker": f"FF{m:02X}", "offset": off,
                        "size": sz})
        off += 2 + sz
        if m == 0xDA:                      # SOS: scan data to FFD9
            i = off
            while i + 1 < len(data):
                if data[i:i + 2] == b"\xff\xd9":
                    eoi = i + 2
                    break
                i += 1
            break
    out["markers"] = markers
    out["eoi"] = eoi
    out["trailer"] = len(data) - eoi if eoi and len(data) > eoi else 0
    if out["trailer"]:
        out["trailer_preview"] = data[eoi:eoi + 64].hex()
    return out, eoi or len(data)


def gif(data):
    out = {"format": "gif"}
    t = data.rfind(b"\x3b")
    out["trailer_marker"] = t
    out["trailer"] = len(data) - t - 1 if t >= 0 and len(data) > t + 1 \
        else 0
    if out["trailer"]:
        out["trailer_preview"] = data[t + 1:t + 65].hex()
    return out, t + 1 if t >= 0 else len(data)


def scan(data):
    if data[:8] == b"\x89PNG\r\n\x1a\n":
        out, end = png(data)
    elif data[:3] == b"\xff\xd8\xff":
        out, end = jpeg(data)
    elif data[:4] == b"GIF8":
        out, end = gif(data)
    else:
        out, end = {"format": "unknown",
                    "note": "no PNG/JPEG/GIF magic — embedded signature "
                            "scan only"}, 0
    emb = _embedded(data, skip_first=8)
    if emb:
        out["embedded_signatures"] = emb
        out["hint"] = ("a second format is embedded — carve it and "
                       "re-run the matching parser")
    out["size"] = len(data)
    return out


def _selftest():
    def chunk(t, b):
        return struct.pack(">I", len(b)) + t + b + \
            struct.pack(">I", zlib.crc32(t + b) & 0xFFFFFFFF)
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
    png = (b"\x89PNG\r\n\x1a\n" + ihdr + chunk(b"tEXt", b"k\x00v")
           + chunk(b"IEND", b"") + b"PK\x03\x04" + b"flag{hidden}")
    d = scan(png)
    assert d["format"] == "png" and d["trailer"] == 16, d
    assert d["embedded_signatures"][0]["format"] == "zip"
    assert not d["crc_bad"]
    jpg = (b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 9
           + b"\xff\xd9" + b"EXTRA")
    d = scan(jpg)
    assert d["format"] == "jpeg" and d["trailer"] == 5, d
    g = b"GIF89a" + b"\x00" * 20 + b"\x3b" + b"tail"
    d = scan(g)
    assert d["trailer"] == 4, d
    print("img_struct selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="image structure scan")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("image path required")
    print(json.dumps(scan(open(a.path, "rb").read()), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
