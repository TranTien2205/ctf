#!/usr/bin/env python3
"""subsetsum.py -- Lagarias-Odlyzko lattice attack on subset-sum.

The knapsack-cipher shape in crypto CTFs: a list of weights and a
target sum, with density n/log2(max weight) low enough (< ~0.64)
that LLL recovers the 0/1 selection. The lattice is the textbook
one: rows e_i with a -N*a_i tail, plus the (0,...,N*s) row; the
embedded short vector is (x_1..x_n, 0) exactly when the weights sum
to s. This builds it, runs the repo's own lll_reduce, and verifies
any candidate row by actually summing it -- a row that fails the
sum is reported, not trusted.

High-density or superincreasing inputs get their own honest paths:
a superincreasing sequence is solved greedily, and a dense instance
reports that the lattice has no reason to isolate the target.

  python3 tools/crypto/subsetsum.py --weights '3,11,4,9,...' --sum 23
  python3 tools/crypto/subsetsum.py --selftest
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import lll  # noqa: E402


def _superincreasing(ws):
    s = 0
    for w in ws:
        if w <= s:
            return False
        s += w
    return True


def solve(weights, target):
    ws = [int(w) for w in weights]
    n = len(ws)
    if n < 3:
        return {"error": "need at least 3 weights"}
    if _superincreasing(ws):
        sel = [0] * n
        rem = target
        for i in range(n - 1, -1, -1):
            if ws[i] <= rem:
                rem -= ws[i]
                sel[i] = 1
        if rem == 0:
            return {"bits": sel, "via": "superincreasing-greedy",
                    "verified": True}
        return {"error": "superincreasing but no exact subset",
                "via": "superincreasing-greedy", "verified": False}
    import math
    density = n / max(1.0, math.log2(max(ws) + 1))
    N = n + 1
    basis = []
    for i in range(n):
        row = [0] * (n + 1)
        row[i] = 1
        row[n] = -N * ws[i]
        basis.append(row)
    basis.append([0] * n + [N * target])
    red = lll.lll_reduce(basis)
    cands = []
    for row in red:
        if row[n] != 0:
            continue
        bits = [abs(c) for c in row[:n]]
        if all(b in (0, 1) for b in bits) and any(bits):
            got = sum(b * w for b, w in zip(bits, ws))
            cands.append({"bits": bits, "sum": got,
                          "verified": got == target})
    good = [c for c in cands if c["verified"]]
    out = {"density": round(density, 3),
           "low_density": density < 0.64,
           "candidates": cands[:5]}
    if good:
        out["bits"] = good[0]["bits"]
        out["via"] = "lagarias-odlyzko"
        out["verified"] = True
    else:
        out["error"] = "no verified subset in reduced basis"
        if density >= 0.64:
            out["note"] = ("density %.2f >= 0.64 -- the LO lattice has"
                           " no reason to isolate the target" % density)
    return out


def _selftest():
    import random
    random.seed(7)
    # superincreasing path
    w_si = [2, 5, 11, 23, 46]
    r = solve(w_si, 30)
    assert r["verified"] and r["bits"] == [1, 1, 0, 1, 0], r
    # low-density random instance: n=8, weights < 2^40 -> density ~0.2
    n = 8
    ws = [random.randrange(1, 1 << 40) for _ in range(n)]
    bits = [random.choice((0, 1)) for _ in range(n)]
    t = sum(b * w for b, w in zip(bits, ws))
    r = solve(ws, t)
    assert r.get("verified"), r
    assert sum(b * w for b, w in zip(r["bits"], ws)) == t
    print("subsetsum selftest: ok (density %.3f)" % r["density"])


def main():
    ap = argparse.ArgumentParser(
        description="subset-sum via Lagarias-Odlyzko lattice")
    ap.add_argument("--weights")
    ap.add_argument("--sum", type=lambda x: int(x, 0))
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.weights or a.sum is None:
        ap.error("--weights and --sum required")
    ws = [int(w, 0) for w in a.weights.replace(",", " ").split()]
    print(json.dumps(solve(ws, a.sum), indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
