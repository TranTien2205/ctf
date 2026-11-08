#!/usr/bin/env python3
"""xor_solve.py — repeating-key and single-byte XOR cracking, stdlib.

tools/crypto/xor.py stops at single-byte and crib-drag; the common CTF
handout is a repeating-key XOR blob. `crack` estimates the key length by
normalised hamming distance over candidate sizes, then solves each key
position as an independent single-byte XOR scored by English letter
frequency plus printable ratio — the classic cryptopals path. `single`
runs the same scorer on a single-byte pad. Every result carries its key
candidate, plaintext preview, and score so a wrong-length answer is
visible, not silently trusted.

    python3 tools/xor_solve.py crack --hex 1b373733...
    python3 tools/xor_solve.py crack --file ct.bin --max-keylen 40
    python3 tools/xor_solve.py single --hex 1b37373331363f78151b7f2b783431333d78397828372d363c78373e783a393b3736
    python3 tools/xor_solve.py --selftest
"""
from __future__ import annotations

import argparse
import base64
import binascii
import json
import sys

_FREQ = ("etaoin shrdluETAOIN SHRDLU")


def _score(pt: bytes) -> float:
    if not pt:
        return -1e9
    good = sum(chr(b).isalpha() or b in (32, 9, 10, 13) for b in pt)
    freq = sum(_FREQ.find(chr(b)) >= 0 for b in pt)
    odd = sum((not chr(b).isalnum()) and chr(b) not in " .,;:'\"!?()-/\n\t"
              for b in pt)
    bad = sum(b < 9 or (13 < b < 32) or b == 127 for b in pt)
    return 2.0 * good + 1.5 * freq - 2.5 * odd - 20.0 * bad


def _hamming(a: bytes, b: bytes) -> int:
    return sum(bin(x ^ y).count("1") for x, y in zip(a, b))


def _best_key_byte(col: bytes, top=3):
    scored = sorted(
        ((_score(bytes(b ^ k for b in col)), k) for k in range(256)),
        key=lambda t: -t[0])
    return scored[:top]


def crack(ct: bytes, max_keylen=40):
    n = len(ct)
    if n < 16:
        return {"error": "under 16 bytes — too short to measure"}
    sizes = []
    for ks in range(2, min(max_keylen, n // 4) + 1):
        blocks = [ct[i:i + ks] for i in range(0, ks * 4, ks)]
        if len(blocks) < 4:
            break
        dists = [_hamming(blocks[i], blocks[i + 1]) / ks
                 for i in range(len(blocks) - 1)]
        sizes.append((sum(dists) / len(dists), ks))
    sizes.sort()
    out = {"keylen_ranking": [{"keylen": k, "norm_dist": round(d, 3)}
                              for d, k in sizes[:6]], "tried": []}
    for _d, ks in sizes[:6]:
        cols = [ct[i::ks] for i in range(ks)]
        key = bytearray()
        per_col = []
        for c in cols:
            best = _best_key_byte(c)
            key.append(best[0][1])
            per_col.append([hex(k) for _s, k in best])
        pt = bytes(b ^ key[i % ks] for i, b in enumerate(ct))
        rec = {"keylen": ks, "key_hex": key.hex(),
               "key_ascii": key.decode("ascii", "replace"),
               "score": round(_score(pt) / max(1, n), 3),
               "plaintext_head": pt[:120].decode("utf-8", "replace"),
               "per_column_top": per_col}
        out["tried"].append(rec)
    # prefer shortest key within epsilon of the top score — a wrong-length
    # key whose columns happen to decode cleanly should not beat the real
    # shorter one on a short ciphertext
    if out["tried"]:
        top = max(r["score"] for r in out["tried"])
        out["best"] = min((r for r in out["tried"] if r["score"] >= top - 0.1),
                          key=lambda r: r["keylen"])
    else:
        out["best"] = None
    out["candidate_only"] = True
    return out


def single(ct: bytes, top=5):
    best = _best_key_byte(ct, top=top)
    return {"candidates": [{"key_hex": hex(k),
                            "score": round(s / max(1, len(ct)), 3),
                            "plaintext_head":
                            bytes(b ^ k for b in ct)[:120].decode("utf-8", "replace")}
                           for s, k in best],
            "candidate_only": True}


def _selftest() -> int:
    pt = (b"Burning 'em, if you ain't quick and nimble\n"
          b"I go crazy when I hear a cymbal") * 2
    key = b"ICE"
    ct = bytes(b ^ key[i % 3] for i, b in enumerate(pt))
    out = crack(ct, max_keylen=10)
    best = out["best"]
    assert best["key_ascii"] == "ICE" or best["keylen"] in (3, 6, 9), best
    s = single(ct)
    assert "candidates" in s
    print("xor_solve selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    for name in ("crack", "single"):
        p = sub.add_parser(name)
        src = p.add_mutually_exclusive_group(required=True)
        src.add_argument("--hex")
        src.add_argument("--b64")
        src.add_argument("--file")
        if name == "crack":
            p.add_argument("--max-keylen", type=int, default=40)
        else:
            p.add_argument("--top", type=int, default=5)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if not args.cmd:
        ap.print_help()
        return 2
    if args.hex:
        ct = binascii.unhexlify(args.hex.strip())
    elif args.b64:
        ct = base64.b64decode(args.b64)
    else:
        ct = open(args.file, "rb").read()
    out = crack(ct, args.max_keylen) if args.cmd == "crack" \
        else single(ct, args.top)
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
