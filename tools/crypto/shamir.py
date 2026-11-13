#!/usr/bin/env python3
"""shamir.py -- Shamir secret sharing combine over GF(p).

CTF secret-sharing challenges hand you k of n shares (x_i, y_i) and
the prime the polynomial lives over; the secret is f(0). This does
the mod-p Lagrange combine directly -- no need for sympy -- and can
also evaluate the reconstructed polynomial at any point to check a
share is consistent (a corrupted share changes the secret).

  python3 tools/crypto/shamir.py --p PRIME --shares '1:y1,2:y2,3:y3'
  python3 tools/crypto/shamir.py --p PRIME --shares '...' --at 7
  python3 tools/crypto/shamir.py --selftest
"""
import argparse
import json


def combine(shares, p, at=0):
    """Lagrange at `at` over GF(p). shares = [(x,y)] with distinct x."""
    acc = 0
    n = len(shares)
    for i, (xi, yi) in enumerate(shares):
        num, den = 1, 1
        for j, (xj, _y) in enumerate(shares):
            if i == j:
                continue
            num = num * ((at - xj) % p) % p
            den = den * ((xi - xj) % p) % p
        acc = (acc + yi % p * num * pow(den, -1, p)) % p
    return acc


def _selftest():
    p = 2**127 - 1
    # f(x) = s + 7x + 42x^2 mod p, s = 0xC0FFEE
    s = 0xC0FFEE
    f = [s, 7, 42]
    def ev(x):
        return (f[0] + f[1] * x + f[2] * x * x) % p
    shares = [(i, ev(i)) for i in (1, 2, 3, 5, 9)]
    assert combine(shares[:3], p) == s
    assert combine([shares[0], shares[2], shares[4]], p) == s
    assert combine(shares[:3], p, at=11) == ev(11)
    # bad share gives a different "secret" -- detected, not hidden
    bad = [(1, shares[0][1]), (2, shares[1][1] + 1), (3, shares[2][1])]
    assert combine(bad, p) != s
    print("shamir selftest: ok")


def main():
    ap = argparse.ArgumentParser(
        description="Shamir SSS combine over GF(p)")
    ap.add_argument("--p", type=lambda x: int(x, 0))
    ap.add_argument("--shares", help="'x:y,x:y,...' hex/dec")
    ap.add_argument("--at", type=lambda x: int(x, 0), default=0)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.p or not a.shares:
        ap.error("--p and --shares required")
    shares = []
    for part in a.shares.split(","):
        x, y = part.split(":")
        shares.append((int(x, 0), int(y, 0)))
    print(json.dumps({"point": a.at,
                      "value": hex(combine(shares, a.p, a.at)),
                      "int": combine(shares, a.p, a.at)}))


if __name__ == "__main__":
    raise SystemExit(main())
