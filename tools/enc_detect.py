#!/usr/bin/env python3
r"""enc_detect.py — layered encoding identification, offline. Stdlib only.

misc-encoding-carrier's job is naming the layer sequence; the skill's
reference lists the shapes but nothing peels them. This walks the input
through a bounded decoder set — the carriers that are mechanically
recognisable (hex, base64, base32, url-quoting, gzip/zlib/zip magic) — and
reports the chain it actually decoded, with a per-layer verdict. It does not
guess: a layer is only reported when it both decodes cleanly and leaves
something a next layer plausibly encoded (printable, or a known magic).
What comes out the far end is text for the agent to read, never a flag claim.

    python3 tools/enc_detect.py 'aGVsbG8='
    python3 tools/enc_detect.py --file blob.bin
    python3 tools/enc_detect.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import binascii
import gzip
import json
import re
import sys
import urllib.parse
import zlib
import zipfile
import io

_MAX_DEPTH = 8
_MAX_BYTES = 4 << 20          # 4 MiB — a bigger blob is a carving job, not a decode job
_PRINTABLE = re.compile(rb"^[\x09\x0a\x0d\x20-\x7e]+$")

_MAGICS = [(b"\x1f\x8b", "gzip"), (b"PK\x03\x04", "zip"), (b"\x78\x9c", "zlib"),
           (b"\x78\xda", "zlib"), (b"\x78\x01", "zlib")]


def _looks_text(b: bytes) -> bool:
    return bool(b) and bool(_PRINTABLE.match(b))


def _try_layer(b: bytes) -> tuple:
    """(decoded, name) or (None, None). Order: least ambiguous first."""
    for magic, name in _MAGICS:
        if b.startswith(magic):
            try:
                if name == "gzip":
                    out = gzip.decompress(b)
                elif name == "zlib":
                    out = zlib.decompress(b)
                else:  # zip: report member names, decode first member
                    zf = zipfile.ZipFile(io.BytesIO(b))
                    names = zf.namelist()
                    return (json.dumps({"zip_members": names}).encode(),
                            f"zip[{len(names)} members: {', '.join(names[:5])}]")
                return out, name
            except Exception:
                return None, None
    t = b.strip()
    # pure-01 strings match the hex alphabet too — try binary first, its
    # output is downstream-scored while hex-of-01s yields valid garbage
    if len(t) >= 16 and re.fullmatch(rb"[01\s]+", t):
        bits = re.sub(rb"\s", b"", t)
        if len(bits) % 8 == 0:
            return bytes(int(bits[i:i + 8], 2)
                       for i in range(0, len(bits), 8)), "binary"
    if len(t) > 4 and re.fullmatch(rb"[0-9a-fA-F\s]+", t):
        try:
            out = binascii.unhexlify(re.sub(rb"\s", b"", t))
            if out:
                return out, "hex"
        except (binascii.Error, ValueError):
            pass
    if len(t) > 4 and re.fullmatch(rb"[A-Za-z0-9+/]+={0,2}", t) and len(t) % 4 == 0:
        try:
            out = base64.b64decode(t, validate=True)
            if out:
                return out, "base64"
        except (binascii.Error, ValueError):
            pass
    if len(t) > 4 and re.fullmatch(rb"[A-Z2-7]+={0,6}", t):
        try:
            pad = (8 - len(t) % 8) % 8
            out = base64.b32decode(t + b"=" * pad)
            if out:
                return out, "base32"
        except (binascii.Error, ValueError):
            pass
    if b"%" in t and re.search(rb"%[0-9a-fA-F]{2}", t):
        out = urllib.parse.unquote_to_bytes(t.decode("ascii", "replace"))
        if out and out != t:
            return out, "url-quoted"
    if len(t) > 8 and re.fullmatch(rb"[\d,;\s]+", t) and b"," in t:
        try:
            vals = [int(x) for x in re.split(rb"[,\s;]+", t.strip()) if x]
            if vals and all(0 <= v <= 255 for v in vals):
                return bytes(vals), "decimal-array"
        except ValueError:
            pass
    if len(t) > 8 and re.fullmatch(rb"([0-3][0-7]{2}|[0-7]{1,2})([,\s]+[0-3]?[0-7]{1,2})*", t):
        try:
            vals = [int(x, 8) for x in re.split(rb"[,\s]+", t.strip()) if x]
            if vals and all(0 <= v <= 255 for v in vals):
                return bytes(vals), "octal-array"
        except ValueError:
            pass
    if len(t) > 4 and re.fullmatch(rb"[!-u]+", t):
        try:
            out = base64.b85decode(t)
            if out:
                return out, "base85"
        except (binascii.Error, ValueError):
            pass
    if len(t) > 8 and re.fullmatch(rb"[.\- /|]+", t) and b"." in t and b"-" in t:
        decoded = _morse(t)
        if decoded:
            return decoded, "morse"
    return None, None


_MORSE = {
    ".-": b"a", "-...": b"b", "-.-.": b"c", "-..": b"d", ".": b"e",
    "..-.": b"f", "--.": b"g", "....": b"h", "..": b"i", ".---": b"j",
    "-.-": b"k", ".-..": b"l", "--": b"m", "-.": b"n", "---": b"o",
    ".--.": b"p", "--.-": b"q", ".-.": b"r", "...": b"s", "-": b"t",
    "..-": b"u", "...-": b"v", ".--": b"w", "-..-": b"x", "-.--": b"y",
    "--..": b"z", ".----": b"1", "..---": b"2", "...--": b"3",
    "....-": b"4", ".....": b"5", "-....": b"6", "--...": b"7",
    "---..": b"8", "----.": b"9", "-----": b"0",
}


def _morse(t: bytes) -> bytes:
    s = t.decode("ascii", "replace").replace("|", " / ")
    out = bytearray()
    for word in s.split(" / "):
        chars = [_MORSE.get(c) for c in word.split()]
        if not chars or any(c is None for c in chars):
            return b""
        out += b"".join(chars) + b" "
    return bytes(out).strip()


def peel(data: bytes) -> dict:
    chain, seen = [], set()
    cur = data[:_MAX_BYTES]
    for _ in range(_MAX_DEPTH):
        sig = hash(cur[:4096])
        if sig in seen:
            chain.append({"layer": "cycle", "note": "decode looped — stopping"})
            break
        seen.add(sig)
        out, name = _try_layer(cur)
        if out is None:
            break
        chain.append({"layer": name, "in_bytes": len(cur), "out_bytes": len(out)})
        cur = out[:_MAX_BYTES]
    result = {"layers": [c["layer"] for c in chain if c["layer"] != "cycle"],
              "depth": len([c for c in chain if c["layer"] != "cycle"]),
              "chain": chain}
    if _looks_text(cur):
        result["decoded"] = cur.decode("utf-8", "replace")[:8192]
        result["final"] = "text"
    elif len(cur) < len(data[:_MAX_BYTES]):
        result["final_hex_head"] = cur[:64].hex()
        result["final"] = "binary (magic checked; needs a format-specific tool)"
    else:
        result["final"] = "no layer recognised — try cipher routing, not decoding"
    return result


def _selftest() -> int:
    inner = b"flag{layers_peeled}"
    enc = base64.b64encode(binascii.hexlify(inner))
    r = peel(enc)
    assert r["layers"] == ["base64", "hex"] and r["decoded"] == inner.decode()
    r2 = peel(gzip.compress(b"flag{zipped}"))
    assert r2["layers"] == ["gzip"] and "flag{zipped}" in r2["decoded"]
    r3 = peel(urllib.parse.quote_plus("flag{url}").encode())
    assert r3["layers"] == ["url-quoted"]
    bits = b"".join(format(b_, "08b").encode() for b_ in b"flag{bin}")
    r4 = peel(bits)
    assert r4["layers"] == ["binary"] and "flag{bin}" in r4["decoded"], r4
    r5b = peel(b"102,108,97,103,123,100,101,99,125")
    assert r5b["layers"] == ["decimal-array"] and "flag{dec}" in r5b["decoded"]
    r5c = peel(b".... . .-.. .-.. --- / .-- --- .-. .-.. -..")
    assert r5c["layers"] == ["morse"] and "hello world" in r5c["decoded"], r5c
    r4 = peel(b"just plain text")
    assert r4["layers"] == [] and r4["final"] == "text"      # already readable
    r5 = peel(b"\x00\x01\x02\x03")
    assert r5["final"].startswith("no layer")              # binary, no magic
    print("enc_detect selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("data", nargs="?", help="string to peel (else stdin, else --file)")
    ap.add_argument("--file", help="read bytes from a file")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.file:
        data = open(args.file, "rb").read()
    elif args.data is not None:
        data = args.data.encode()
    elif not sys.stdin.isatty():
        data = sys.stdin.buffer.read()
    else:
        ap.print_help()
        return 2
    print(json.dumps(peel(data), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
