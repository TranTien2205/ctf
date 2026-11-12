#!/usr/bin/env python3
"""qr_decode.py -- QR/barcode decode for misc+forensic image handouts.

A flag-in-a-QR needs a decoder, and the obvious ones (zbarimg) are
external. This tries the decoders actually present, in order:
cv2.QRCodeDetector (detectAndDecode + multi), then pyzbar (which also
does Code128/EAN/DataMatrix/Aztec). Each hit reports which backend
decoded it; with neither installed it says so instead of pretending
the image was empty.

  python3 tools/forensics/qr_decode.py code.png
  python3 tools/forensics/qr_decode.py --selftest
"""
import argparse
import json
import re
import sys


def _cv2(path):
    import cv2
    img = cv2.imread(path)
    if img is None:
        return []
    det = cv2.QRCodeDetector()
    out = []
    try:
        ok, multi, _pts, _q = det.detectAndDecodeMulti(img)
        if ok:
            out += [t for t in multi if t]
    except cv2.error:
        pass
    single = det.detectAndDecode(img)[0]
    if single and single not in out:
        out.append(single)
    return [{"backend": "cv2", "type": "QR", "text": t} for t in out]


def _pyzbar(path):
    from pyzbar.pyzbar import decode
    from PIL import Image
    return [{"backend": "pyzbar", "type": o.type,
             "text": o.data.decode("utf-8", "replace")}
            for o in decode(Image.open(path))]


def flag_hits(hits):
    return [h["text"] for h in hits
            if re.search(r"[A-Za-z0-9_]+\{[^}]{3,}\}", h["text"])]


def _selftest():
    import os
    import struct
    import tempfile
    import zlib
    # flag extraction is the plumbing that must not drift
    hits = [{"text": "see flag{qr_carry_ok}", "type": "QR", "backend": "x"},
            {"text": "unrelated payload", "type": "QR", "backend": "x"}]
    assert flag_hits(hits) == ["see flag{qr_carry_ok}"]
    # and an empty image reports no codes instead of inventing one
    def png(rgb, w, h):
        raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))
        def chunk(t, d):
            c = t + d
            return struct.pack(">I", len(d)) + c + \
                struct.pack(">I", zlib.crc32(c) & 0xFFFFFFFF)
        ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
        return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) \
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b"")
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(png((255, 255, 255), 8, 8))
        p = f.name
    try:
        res = decode_all(p)
    finally:
        os.unlink(p)
    assert res["codes"] == [] or res.get("error"), res
    print("qr_decode selftest: ok")


def decode_all(path):
    try:
        hits = _cv2(path)
    except ImportError:
        hits = []
    try:
        for h in _pyzbar(path):
            if not any(h["text"] == x["text"] for x in hits):
                hits.append(h)
    except ImportError:
        pass
    except Exception as exc:
        return {"codes": hits,
                "note": "pyzbar failed on this image: %s" % exc}
    if hits:
        return {"codes": hits, "flag_strings": flag_hits(hits)}
    try:
        import cv2  # noqa: F401
        have_cv2 = True
    except ImportError:
        have_cv2 = False
    try:
        import pyzbar  # noqa: F401
        have_zbar = True
    except ImportError:
        have_zbar = False
    if not (have_cv2 or have_zbar):
        return {"error": "no QR backend: needs cv2 or pyzbar",
                "codes": []}
    return {"codes": [], "note": "decoders present; no code found"}


def main():
    ap = argparse.ArgumentParser(description="QR/barcode decode")
    ap.add_argument("path", nargs="?")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.path:
        ap.error("image path required")
    print(json.dumps(decode_all(a.path), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
