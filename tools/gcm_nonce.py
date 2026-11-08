#!/usr/bin/env python3
"""GCM forbidden attack: recover GHASH key H from a reused nonce, forge tags.

crypto-triage's last tool-less row. Two ciphertexts C1, C2 with tags
T1, T2 under one nonce give T1 ^ T2 = GHASH_H(C1) ^ GHASH_H(C2) — a
polynomial in H over GF(2^128) whose roots are the candidate H values.
Once H is known, J0mask = T1 ^ GHASH_H(C1) lets this tool mint a valid
tag for an arbitrary same-nonce ciphertext.

  python3 tools/gcm_nonce.py recover --ct1 HEX --tag1 HEX --ct2 HEX --tag2 HEX
  python3 tools/gcm_nonce.py forge --ct HEX --tag HEX --h HEX --new-ct HEX
  python3 tools/gcm_nonce.py --selftest

Polynomial arithmetic runs over GF(2^128) with the GCM reduction
polynomial (x^128 + x^7 + x^2 + x + 1); root finding squares the
indeterminate through the Frobenius chain mod P, keeps the linear
factor part, then splits it with the field trace — deterministic work
bounded by ciphertext block count. --aad1/--aad2 for AAD; unequal
ciphertext lengths are handled (the length block does not cancel).

recover lists every root; a wrong H just produces forged tags the
target rejects — that rejection is the falsifier, never trust output
that was not verified against a third same-nonce pair or the target.
"""
import argparse, json, random, sys

# ---- GF(2^128), GCM's bit-reflected convention ------------------------

R = 0xE1 << 120  # reduction polynomial after reflection
ONE = 1 << 127   # multiplicative identity in the reflected convention


def gmul(a, b):
    z, v = 0, b
    for i in range(128):
        if (a >> (127 - i)) & 1:
            z ^= v
        v = (v >> 1) ^ (R if v & 1 else 0)
    return z


def gpow(a, n):
    r = ONE
    while n:
        if n & 1:
            r = gmul(r, a)
        a = gmul(a, a)
        n >>= 1
    return r


def ghash(h, aad, ct):
    """Real GHASH: X_i = (X_{i-1} ^ block) * H, last block is
    64-bit aad-bitlen || 64-bit ct-bitlen."""
    def blocks(d):
        d = d + b"\x00" * (-len(d) % 16)
        return [int.from_bytes(d[i:i + 16], "big")
                for i in range(0, len(d), 16)]
    x = 0
    for b in blocks(aad) + blocks(ct):
        x = gmul(x ^ b, h)
    lb = (len(aad) * 8).to_bytes(8, "big") + (len(ct) * 8).to_bytes(8, "big")
    return gmul(x ^ int.from_bytes(lb, "big"), h)


def ghash_poly(aad, ct):
    """GHASH as a polynomial over GF(2^128): coeffs[k] multiplies H^k.
    GHASH = B_1 H^n ^ B_2 H^{n-1} ^ ... ^ B_n H ^ len*H — so the length
    block sits at H^1 and H^0 is always 0."""
    def pad(d):
        return d + b"\x00" * (-len(d) % 16)
    bl = [int.from_bytes(pad(aad)[i:i + 16], "big")
          for i in range(0, len(pad(aad)), 16)] + \
         [int.from_bytes(pad(ct)[i:i + 16], "big")
          for i in range(0, len(pad(ct)), 16)]
    if not bl:
        bl = [0]
    lb = (len(aad) * 8).to_bytes(8, "big") + (len(ct) * 8).to_bytes(8, "big")
    n = len(bl) + 1
    coeffs = [0] * (n + 1)
    for i, b in enumerate(bl):
        coeffs[n - i] = b
    coeffs[1] = int.from_bytes(lb, "big")
    return coeffs


# ---- polynomials over GF(2^128): lists, coeffs[k] = coeff of X^k ------

def _n(p):
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def padd(a, b):
    n = max(len(a), len(b))
    return _n([(a[i] if i < len(a) else 0) ^ (b[i] if i < len(b) else 0)
               for i in range(n)])


def pmul(a, b):
    r = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    r[i + j] ^= gmul(ai, bj)
    return _n(r)


def _lead_inv(m):
    return ONE if m[-1] == ONE else gpow(m[-1], (1 << 128) - 2)


def pmod(a, m):
    return pdivmod(a, m)[1]


def pdivmod(a, m):
    a = a[:]
    q = [0]
    dm = len(m) - 1
    inv = _lead_inv(m)
    while len(a) - 1 >= dm:
        k = len(a) - 1 - dm
        c = gmul(a[-1], inv)
        if len(q) <= k:
            q += [0] * (k + 1 - len(q))
        q[k] ^= c
        for i, mc in enumerate(m):
            if mc:
                a[i + k] ^= gmul(c, mc)
        _n(a)
    return _n(q), a


def pgcd(a, b):
    a, b = a[:], b[:]
    while b != [0]:
        _, a = pdivmod(a, b)
        a, b = b, a
    lc = a[-1]
    if lc != ONE:
        inv = gpow(lc, (1 << 128) - 2)
        a = [gmul(c, inv) for c in a]
    return a


def psquare(p):
    """Frobenius square: coefficients squared, exponents doubled."""
    r = [0] * (2 * len(p) - 1)
    for i, c in enumerate(p):
        r[2 * i] = gmul(c, c)
    return _n(r)


def pfrob_chain(p):
    """X^{2^128} mod P: start from X, square 128 times."""
    x = [0, 1]
    for _ in range(128):
        x = pmod(psquare(x), p)
    return x


def ptrace(ax, p):
    """Tr(ax) = sum_{i=0}^{127} (ax)^{2^i} mod P — the CZ splitting tool."""
    cur = pmod(ax, p)
    t = cur[:]
    for _ in range(127):
        cur = pmod(psquare(cur), p)
        t = padd(t, cur)
    return t


def roots_of(p):
    """All roots of P in GF(2^128)."""
    f = padd(pfrob_chain(p), [0, 1])  # X^{2^128} - X mod P
    g = pgcd(f, p)
    out = []

    def split(q, depth=0):
        if len(q) <= 2:
            if len(q) == 2:
                out.append(gmul(q[0], _lead_inv(q)))  # root of q1 X + q0
            return
        if depth > 24:
            return
        rnd = random.Random(0xC0FFEE + depth * 7919 + len(out))
        for _ in range(64):
            a = rnd.getrandbits(128)
            t = ptrace([0, a], q)
            g2 = pgcd(t, q)
            if 1 < len(g2) < len(q):
                split(g2, depth + 1)
                split(pdivmod(q, g2)[0], depth + 1)
                return
    split(g)
    return out


def peval(coeffs, h):
    acc = 0
    for c in reversed(coeffs):
        acc = gmul(acc, h) ^ c
    return acc


def _unhex(s):
    return bytes.fromhex(s.replace("0x", "").strip())


def recover(ct1, tag1, ct2, tag2, aad1=b"", aad2=b""):
    p1, p2 = ghash_poly(aad1, ct1), ghash_poly(aad2, ct2)
    diff = padd(p1, p2)
    diff[0] ^= tag1 ^ tag2
    cand = roots_of(diff)
    # verify each candidate by predicting tag2 from tag1
    ok = []
    for h in cand:
        j0mask = ghash(h, aad1, ct1) ^ tag1
        if ghash(h, aad2, ct2) ^ j0mask == tag2:
            ok.append({"h": "%032x" % h, "j0mask": "%032x" % j0mask})
    return {"candidates": ok, "roots_tested": len(cand),
            "note": "each candidate predicts both tags; forge with "
                    "--h and verify on the target — a rejected forged "
                    "tag falsifies that root"}


def forge(ct, tag, h, new_ct, aad=b""):
    j0mask = ghash(h, aad, ct) ^ tag
    return {"new_tag": "%032x" % (ghash(h, aad, new_ct) ^ j0mask),
            "j0mask": "%032x" % j0mask,
            "note": "valid only under the same nonce as the source pair"}


def _selftest() -> int:
    h = 0x66E94BD4EF8A2C3B884CFA59CA342B2E
    j0mask = 0xA54B2C1D0EF98765
    ct1 = bytes(range(32))
    ct2 = bytes(range(64, 96))
    t1 = ghash(h, b"", ct1) ^ j0mask
    t2 = ghash(h, b"", ct2) ^ j0mask
    # polynomial evaluation agrees with iterative GHASH
    assert peval(ghash_poly(b"", ct1), h) == ghash(h, b"", ct1)
    r = recover(ct1, t1, ct2, t2)
    hs = {c["h"] for c in r["candidates"]}
    assert "%032x" % h in hs, (hs, "%032x" % h)
    f = forge(ct1, t1, h, bytes(range(96, 128)))
    assert int(f["new_tag"], 16) == ghash(h, b"", bytes(range(96, 128))) ^ j0mask
    # unequal-length pair (length block does not cancel) must still work
    ct3 = bytes(range(48))
    t3 = ghash(h, b"", ct3) ^ j0mask
    r2 = recover(ct1, t1, ct3, t3)
    assert "%032x" % h in {c["h"] for c in r2["candidates"]}
    print("gcm_nonce selftest: ok")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", choices=["recover", "forge"],
                    default="recover")
    for f in ("--ct1", "--tag1", "--ct2", "--tag2", "--ct", "--tag",
              "--h", "--new-ct", "--aad1", "--aad2"):
        ap.add_argument(f, default="")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.cmd == "recover":
        need = (a.ct1, a.tag1, a.ct2, a.tag2)
        if not all(need):
            ap.error("recover needs --ct1 --tag1 --ct2 --tag2")
        out = recover(_unhex(a.ct1), int(a.tag1, 16),
                      _unhex(a.ct2), int(a.tag2, 16),
                      _unhex(a.aad1), _unhex(a.aad2))
    else:
        need = (a.ct, a.tag, a.h, a.new_ct)
        if not all(need):
            ap.error("forge needs --ct --tag --h --new-ct")
        out = forge(_unhex(a.ct), int(a.tag, 16), int(a.h, 16),
                    _unhex(a.new_ct), _unhex(a.aad1))
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
