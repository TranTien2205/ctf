#!/usr/bin/env python3
"""Franklin-Reiter related-message attack on RSA.

Shape: two ciphertexts under the same (n, e) whose plaintexts are
linearly related, m2 = a*m1 + b (mod n). Typical handout: a flag
padded with a counter, or "message sent twice with a known prefix
difference". Then m1 is a common root of

    f(x) = x^e - c1          (mod n)
    g(x) = (a*x + b)^e - c2  (mod n)

so gcd(f, g) over Z/nZ is the linear factor (x - m1).

Z/nZ is a ring, not a field: the Euclidean step can hit a leading
coefficient that does not invert mod n. When that happens gcd(lc, n)
is a proper factor of n -- which is also a win, so the tool reports
it instead of dying.

    python3 tools/crypto/franklin_reiter.py --n N --e 3 --a 1 --b B \
        --c1 C1 --c2 C2

All integers decimal or 0x-hex. Prints JSON with `m` (int), `text`
(best-effort decode) and `note`. --selftest runs a real RSA
encrypt-then-recover loop offline.
"""
import argparse
import json
import math
import sys


def _trim(p, n):
    while p and p[-1] % n == 0:
        p.pop()
    return [c % n for c in p]


def _mul(a, b, n):
    out = [0] * (len(a) + len(b) - 1)
    for i, x in enumerate(a):
        if x:
            for j, y in enumerate(b):
                out[i + j] = (out[i + j] + x * y) % n
    return _trim(out, n)


def _mod(f, g, n):
    """f mod g over Z/n; returns (remainder, factor_or_None)."""
    f = _trim(f, n)
    dg = len(g) - 1
    while len(f) - 1 >= dg and f:
        lc = f[-1]
        g_lc = g[-1]
        d = math.gcd(lc, n)
        if d == n:
            f.pop()
            continue
        inv = pow(g_lc, -1, n) if math.gcd(g_lc, n) == 1 else None
        if inv is None:
            return f, math.gcd(g_lc, n)
        k = lc * inv % n
        shift = len(f) - 1 - dg
        for j in range(len(g)):
            f[shift + j] = (f[shift + j] - k * g[j]) % n
        _trim(f, n)
    return f, None


def _pgcd(a, b, n):
    a, b = _trim(a, n), _trim(b, n)
    while b:
        r, fac = _mod(a, b, n)
        if fac is not None:
            return None, fac
        a, b = b, _trim(r, n)
    return a, None


def _powmod(poly, e, modulus, n):
    """poly**e mod modulus over Z/n."""
    acc = [1]
    base = _trim(poly, n)
    while e:
        if e & 1:
            acc = _mul(acc, base, n)
            acc, fac = _mod(acc, modulus, n)
            if fac is not None:
                return None, fac
        e >>= 1
        if e:
            base = _mul(base, base, n)
            base, fac = _mod(base, modulus, n)
            if fac is not None:
                return None, fac
    return acc, None


def franklin_reiter(n, e, a, b, c1, c2):
    """Recover m1 from c1 = m1^e, c2 = (a*m1+b)^e (mod n).

    Returns dict with m, or factor_of_n when a non-invertible
    leading coefficient split n (still a solve), or a note."""
    if a % n == 0:
        return {"ok": False, "note": "a ≡ 0 (mod n): m2 is constant, attack does not apply"}
    f = [(-c1) % n] + [0] * (e - 1) + [1]              # x^e - c1
    lin = [b % n, a % n]                              # a*x + b
    g, fac = _powmod(lin, e, f, n)
    if fac is not None:
        return {"ok": True, "factor_of_n": fac}
    g = _trim([(g[0] - c2) % n] + g[1:], n)           # (ax+b)^e - c2 mod f
    d, fac = _pgcd(f, g, n)
    if fac is not None:
        return {"ok": True, "factor_of_n": fac}
    if d is None or len(d) != 2:
        return {"ok": False, "degree": len(d or []) - 1,
                "note": "gcd is not linear; plaintexts may not be related as claimed"}
    # d = (d0 + d1*x); monic-ify; root m = -d0 * d1^-1
    if math.gcd(d[1], n) != 1:
        fac = math.gcd(d[1], n)
        return {"ok": True, "factor_of_n": fac}
    m = (-d[0] * pow(d[1], -1, n)) % n
    return {"ok": True, "m": m}


def _int(s):
    return int(s, 0)


def _to_bytes(m):
    ln = (m.bit_length() + 7) // 8 or 1
    return m.to_bytes(ln, "big")


def _selftest():
    p = 0x800000000000C61FD3A5F7E2B9D4F1CF
    q = 0x80000000004E2B7C3D8A5E61B7C9F36D
    # 128-bit primes ≡ 2 mod 3: n=255 bits > 192-bit message, unique roots
    n = p * q
    e = 3
    a, b = 1, 0x1122334455667788
    m1 = int.from_bytes(b"flag{franklin_reiter_ok}", "big")
    m2 = (a * m1 + b) % n
    c1, c2 = pow(m1, e, n), pow(m2, e, n)
    got = franklin_reiter(n, e, a, b, c1, c2)
    assert got.get("m") == m1, got
    # unrelated ciphertexts must NOT yield a linear gcd claiming m
    c3 = pow((m1 + 0xABCDEF) % n, e, n)
    bad = franklin_reiter(n, e, a, b, c1, c3)
    assert not (bad.get("ok") and bad.get("m")), bad
    print("franklin_reiter selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="Franklin-Reiter related-message RSA attack")
    ap.add_argument("--n", type=_int, help="modulus")
    ap.add_argument("--e", type=int, default=3)
    ap.add_argument("--a", type=_int, default=1, help="linear relation m2 = a*m1 + b")
    ap.add_argument("--b", type=_int, default=0)
    ap.add_argument("--c1", type=_int)
    ap.add_argument("--c2", type=_int)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    for k in ("n", "c1", "c2"):
        if getattr(args, k) is None:
            ap.error(f"--{k} required")
    out = franklin_reiter(args.n, args.e, args.a, args.b, args.c1, args.c2)
    if out.get("m") is not None:
        raw = _to_bytes(out["m"])
        out["hex"] = raw.hex()
        try:
            out["text"] = raw.decode()
        except UnicodeDecodeError:
            out["text"] = None
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
