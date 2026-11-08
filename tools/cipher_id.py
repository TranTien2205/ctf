#!/usr/bin/env python3
"""cipher_id.py — classical-cipher measurements for crypto-classical.

The class's first move is measurement, not guessing: Index of
Coincidence separates English-frequency text (monoalphabetic or
transposition, ~0.066) from smoothed polyalphabetic (~0.038); a Caesar
chi-squared sweep answers the single-shift case outright; Kasiski
repeated-ngram distances estimate the key period for Vigenere-family;
and an English-frequency histogram on otherwise unreadable text points
at transposition. This prints all of them for a ciphertext on stdin or
--text, with family CANDIDATES — the reference decides the attack.

    python3 tools/cipher_id.py --text 'WKHHAJ...'
    cat cipher.txt | python3 tools/cipher_id.py
    python3 tools/cipher_id.py --selftest
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter

_FREQ = [8.167, 1.492, 2.782, 4.253, 12.702, 2.228, 2.015, 6.094, 6.966,
         0.153, 0.772, 4.025, 2.406, 6.749, 7.507, 1.929, 0.095, 5.987,
         6.327, 9.056, 2.758, 0.978, 2.360, 0.150, 1.974, 0.074]


def _ic(text):
    n = len(text)
    if n < 2:
        return 0.0
    c = Counter(text)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1))


def _chi2(text):
    n = len(text)
    if n == 0:
        return 1e9
    c = Counter(text)
    return sum(((c.get(chr(65 + i), 0) + c.get(chr(97 + i), 0) - _FREQ[i] * n / 100) ** 2)
               / (_FREQ[i] * n / 100) for i in range(26))


def _caesar_sweep(text):
    best, best_s = 1e18, None
    for s in range(26):
        dec = "".join(chr((ord(c) - 65 - s) % 26 + 65) if c.isupper() else
                      chr((ord(c) - 97 - s) % 26 + 97) if c.islower() else c
                      for c in text)
        ch = _chi2(dec)
        if ch < best:
            best, best_s = ch, s
    return best_s, round(best, 1)


def _kasiski(text, n=3):
    dists = []
    for i in range(len(text) - n):
        gram = text[i:i + n]
        j = text.find(gram, i + n)
        if j > i:
            dists.append(j - i)
    if not dists:
        return []
    fac = Counter()
    for d in dists:
        for k in range(2, 21):
            if d % k == 0:
                fac[k] += 1
    return [k for k, _ in fac.most_common(4)]


def identify(text) -> dict:
    t = "".join(c for c in text if c.isalpha())
    if len(t) < 20:
        return {"note": "under 20 letters — measurements are noise", "len": len(t)}
    ic = _ic(t.upper())
    shift, chi = _caesar_sweep(t)
    periods = _kasiski(t.upper())
    out = {"len": len(t), "ic": round(ic, 4), "caesar_best_shift": shift,
           "caesar_chi2": chi, "kasiski_periods": periods}
    cands = []
    if chi < 150:
        cands.append({"family": "caesar-or-single-shift",
                      "signal": f"chi2 {chi} at shift {shift} — try decrypting shift {shift}"})
    if ic > 0.058 and chi >= 150:
        cands.append({"family": "monoalphabetic-or-transposition",
                      "signal": f"IC {round(ic, 3)} ≈ English — substitution keeps "
                                "freqs, transposition keeps letters; compare "
                                "digram order to tell them apart"})
    if ic <= 0.048 and periods:
        cands.append({"family": "polyalphabetic-vigenere-family",
                      "signal": f"IC {round(ic, 3)} smoothed; Kasiski periods {periods} "
                                "— split by period, solve each column as Caesar"})
    if not cands:
        out["note"] = ("measurements inconclusive — could be homophonic, "
                       "encoded-not-cipher (route to enc_detect), or too short")
    out["family_candidates"] = cands
    out["candidate_only"] = True
    return out


def _selftest() -> int:
    plain = ("the quick brown fox jumps over the lazy dog and then runs "
             "far away through the forest where the wild things are") * 3
    caesar = "".join(chr((ord(c) - 97 + 3) % 26 + 97) if c.isalpha() else c
                     for c in plain)
    out = identify(caesar)
    fams = {c["family"] for c in out["family_candidates"]}
    assert "caesar-or-single-shift" in fams, out
    assert out["caesar_best_shift"] == 3, out
    # vigenere 'key' on the same text: ic should fall vs caesar
    key = "key"
    vig = "".join(chr((ord(c) - 97 + (ord(key[i % 3]) - 97)) % 26 + 97)
                  if c.isalpha() else c
                  for i, c in enumerate(plain))
    out2 = identify(vig)
    assert out2["ic"] < out["ic"], (out["ic"], out2["ic"])
    print("cipher_id selftest: ok")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--text", help="ciphertext (default: read stdin)")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return _selftest()
    text = args.text if args.text is not None else sys.stdin.read()
    print(json.dumps(identify(text), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
