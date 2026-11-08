#!/usr/bin/env python3
"""hash_id.py — name the hash format and the cheapest first attack. Stdlib only.

The first action on any 'crack this' handout is naming the format; getting it
wrong spends minutes trying sha256 against an NTLM. This maps length, charset
and signature to the candidate family, says whether a salt is present (a
salted format changes the whole attack), and suggests a hashcat-mode and a
first move. It identifies formats — it does not claim the hash is crackable,
and it never guesses a plaintext.

    python3 tools/hash_id.py 5f4dcc3b5aa765d61d8327deb882cf99
    python3 tools/hash_id.py --file hashes.txt
    python3 tools/hash_id.py --selftest
"""
from __future__ import annotations

import argparse
import json
import re
import sys

# (pattern, family, salted, hashcat_mode, first move)
_SIGS = [
    (r"^\$2[abxy]\$\d{2}\$[./A-Za-z0-9]{53}$", "bcrypt", True, 3200,
     "dictionary; cost factor is in the hash — brute force is not the move"),
    (r"^\$6\$", "sha512crypt", True, 1800,
     "dictionary with rules; rounds field may follow the salt"),
    (r"^\$5\$", "sha256crypt", True, 7400, "dictionary with rules"),
    (r"^\$1\$", "md5crypt", True, 500, "fast dictionary — md5crypt is cheap"),
    (r"^\$y\$", "yescrypt", True, None,
     "hashcat supports it (mode for yescrypt); dictionary only"),
    (r"^\$argon2(id|i|d)\$", "argon2", True, None,
     "memory-hard — dictionary only, tiny candidate space"),
    (r"^\$P\$[./A-Za-z0-9]{31}$", "phpass/wordpress", True, 400, "dictionary"),
    (r"^\$apr1\$", "apache md5", True, 1600, "dictionary"),
    (r"^\$krb5", "kerberos", True, None,
     "AS-REP/TGS roast — mode depends on etype in the hash"),
    (r"^0x0100[0-9a-fA-F]{88,}$", "mssql (salted sha1)", True, 131,
     "salt is inside the blob — hashcat splits it"),
    (r"^[a-f0-9]{32}:[a-z0-9]+$", "md5 + salt (joomla-style)", True, 10,
     "salt after the colon"),
]

_HEX_LEN = {
    8:  [("crc32/adler", False, None, "not a password hash — check it is not a checksum")],
    16: [("md4 / ntlm / lm-half", False, 1000, "NTLM cracks fast; try dictionary + rules"),
         ("mysql4.1-old", False, 200, "legacy mysql")],
    32: [("md5 / ntlm / md4", False, 0, "dictionary+rules; NTLM is mode 1000"),
         ("md5(unix)-crypt-raw", True, 500, "if a $1$ prefix was stripped")],
    40: [("sha1", False, 100, "dictionary+rules"),
         ("ripemd160", False, 6000, "dictionary")],
    56: [("sha224", False, 1300, "dictionary"),
         ("sha3-224", False, 17300, "dictionary")],
    64: [("sha256", False, 1400, "dictionary+rules"),
         ("sha3-256", False, 17400, "dictionary"),
         ("blake2s-256", False, None, "dictionary")],
    80: [("ripemd320", False, None, "rare — confirm before spending cycles")],
    96: [("sha384", False, 10800, "dictionary"),
         ("sha3-384", False, 17500, "dictionary")],
    128: [("sha512", False, 1700, "dictionary+rules"),
          ("sha3-512", False, 17600, "dictionary"),
          ("whirlpool", False, 6100, "dictionary")],
}


def identify(text: str) -> dict:
    t = text.strip()
    out = {"input_head": t[:24] + ("…" if len(t) > 24 else ""), "candidates": []}
    for pat, family, salted, mode, move in _SIGS:
        if re.match(pat, t, re.I):
            out["candidates"].append({"family": family, "salted": salted,
                                      "hashcat_mode": mode, "first_move": move})
            break
    if not out["candidates"]:
        if re.fullmatch(r"[0-9a-fA-F]+", t) and len(t) in _HEX_LEN:
            for family, salted, mode, move in _HEX_LEN[len(t)]:
                out["candidates"].append({"family": family, "salted": salted,
                                          "hashcat_mode": mode, "first_move": move})
        elif t.count(".") == 2 and all(re.fullmatch(r"[A-Za-z0-9_=-]+", p) for p in t.split(".")):
            out["candidates"].append({"family": "JWT — not a hash; tools/web/jwt_forge.py "
                                               "or session_dissect.py is the route",
                                      "salted": None, "hashcat_mode": None,
                                      "first_move": "decode, do not crack"})
        elif re.fullmatch(r"[A-Za-z0-9+/]+={0,2}", t) and len(t) >= 16:
            import base64
            try:
                raw = base64.b64decode(t)
                out["candidates"].append(
                    {"family": f"base64 blob ({len(raw)} raw bytes) — decode first, "
                              "then re-run this tool on the hex",
                     "salted": None, "hashcat_mode": None,
                     "first_move": "base64 -d, then hex-dump"})
            except Exception:
                pass
    if not out["candidates"]:
        out["candidates"].append({"family": "unrecognised", "salted": None,
                                  "hashcat_mode": None,
                                  "first_move": "check length/charset by hand or route "
                                               "to enc_detect — it may be an encoding"})
    out["note"] = "identification only — salted formats and KDFs bound the attack before it starts"
    return out


def _selftest() -> int:
    cases = [("5f4dcc3b5aa765d61d8327deb882cf99", "md5"),
             ("aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d", "sha1"),
             ("$2b$12$" + "a" * 53, "bcrypt"),
             ("$6$rounds=5000$salt$" + "a" * 86, "sha512crypt"),
             ("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
              "sha256")]
    for text, want in cases:
        got = identify(text)["candidates"][0]["family"]
        assert want.split("/")[0].split(" ")[0] in got, (text, got)
    assert "JWT" in identify("aaa.bbb.ccc")["candidates"][0]["family"]
    assert identify("zzz")["candidates"][0]["family"] == "unrecognised"
    print("hash_id selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("hash", nargs="?")
    ap.add_argument("--file", help="one hash per line")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    if args.file:
        out = []
        for line in open(args.file, encoding="utf-8", errors="replace"):
            if line.strip():
                out.append(identify(line))
        print(json.dumps(out, indent=1))
        return 0
    if not args.hash:
        ap.print_help()
        return 2
    print(json.dumps(identify(args.hash), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
