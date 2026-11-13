#!/usr/bin/env python3
"""Smart's attack on anomalous elliptic curves.

Shape: ECDLP over E(F_p) with #E(F_p) == p (anomalous). The
Semaev-Smart/Araki-Satoh reduction maps the curve discrete log to a
p-adic division -- the dlog falls out of two p-adic expansions, no
generic dlog cost. The check itself is the falsifier: count the
points; if #E != p the attack does not apply and this tool says so
instead of trying.

    python3 tools/crypto/smart_attack.py --p P --a A --b B \
        --gx X --gy Y --qx X --qy Y [--order N]

Lifts P, Q to E(Q_p) at precision 2 via Hensel on the y coordinate,
multiplies by p with exact rational arithmetic, and recovers
k = t_pQ / t_pP (mod p) where t = -x/y. --order lets the caller pass
the known count; without it the tool refuses rather than inventing
one -- point counting is the challenger's job (or sagemath).

--selftest finds a small anomalous curve by brute-force count and
runs the full reduction offline.
"""
import argparse
import json
import sys
from fractions import Fraction


def _add(P, Q, a):
    """E(Q_p) addition with exact rationals; None is the point at
    infinity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y1 + y2 == 0:
            return None
        s = (3 * x1 * x1 + a) / (2 * y1)
    else:
        s = (y2 - y1) / (x2 - x1)
    x3 = s * s - x1 - x2
    return x3, s * (x1 - x3) - y1


def _mul(k, P, a):
    R = None
    A = P
    while k:
        if k & 1:
            R = _add(R, A, a)
        A = _add(A, A, a)
        k >>= 1
    return R


def _lift(P, p, a, b):
    """Hensel-lift y to precision p^2: y' = y + t·p with
    y'^2 == x^3 + a x + b (mod p^2). x stays put."""
    x, y = P
    corr = (x * x * x + a * x + b - y * y) // p
    t = corr * pow(2 * y, -1, p) % p
    return Fraction(x), Fraction(y + t * p)


def smart_dlog(P, Q, p, a, b):
    """Recover k with Q = kP on an anomalous E(F_p)."""
    lp = _lift(P, p, a, b)
    lq = _lift(Q, p, a, b)
    pp = _mul(p, lp, a)
    pq = _mul(p, lq, a)
    if pp is None or pq is None:
        return {"ok": False,
                "note": "p*lifted_point landed at infinity -- "
                        "curve is not anomalous or lift failed"}
    # kernel points have v(x)=-2, v(y)=-3 so t = -x/y has v(t)=1;
    # the RATIO t_q/t_p is a p-adic unit == k (mod p). Fractions
    # cancel the common p, then reduce mod p directly.
    tp = -pp[0] / pp[1]
    tq = -pq[0] / pq[1]
    if tp == 0:
        return {"ok": False, "note": "t_p == 0 -- degenerate lift"}
    r = tq / tp
    den = r.denominator
    if den % p == 0:
        return {"ok": False,
                "note": "ratio denominator divisible by p -- "
                        "precision-2 lift too weak for this curve"}
    k = (r.numerator % p) * pow(den % p, -1, p) % p
    return {"ok": True, "k": k}


def _count_points(p, a, b):
    """Brute-force #E(F_p); only sane for small p (selftest use)."""
    cnt = 1  # point at infinity
    for x in range(p):
        rhs = (x * x * x + a * x + b) % p
        if rhs == 0:
            cnt += 1
        elif pow(rhs, (p - 1) // 2, p) == 1:
            cnt += 2
    return cnt


def _selftest():
    # find a small anomalous curve deterministically
    found = None
    p = 233
    while p < 2000 and not found:
        # primality: small trial division
        if all(p % d for d in range(2, int(p ** 0.5) + 1)):
            for a in range(0, 6):
                for b in range(1, 8):
                    if (4 * a ** 3 + 27 * b * b) % p == 0:
                        continue
                    if _count_points(p, a, b) == p:
                        found = (p, a, b)
                        break
                if found:
                    break
        p += 1
    assert found, "no small anomalous curve under 2000 -- unexpected"
    p, a, b = found
    # pick a generator: any point works on an anomalous curve
    G = None
    for x in range(p):
        rhs = (x ** 3 + a * x + b) % p
        for y in range(p):
            if y * y % p == rhs:
                G = (x, y)
                break
        if G:
            break
    k_true = 17
    # Q = k*G over F_p
    def add_mod(P, Q):
        if P is None:
            return Q
        if Q is None:
            return P
        x1, y1 = P
        x2, y2 = Q
        if x1 == x2:
            if (y1 + y2) % p == 0:
                return None
            s = (3 * x1 * x1 + a) * pow(2 * y1, -1, p) % p
        else:
            s = (y2 - y1) * pow((x2 - x1) % p, -1, p) % p
        x3 = (s * s - x1 - x2) % p
        return x3, (s * (x1 - x3) - y1) % p
    Qp_ = None
    for _ in range(k_true):
        Qp_ = add_mod(Qp_, G)
    out = smart_dlog(G, Qp_, p, a, b)
    assert out.get("k") == k_true, (out, k_true, found)
    print("smart_attack selftest: ok (p=%d, #E=p=%d)" % (p, p))


def _int(s):
    return int(s, 0)


def main():
    ap = argparse.ArgumentParser(description="Smart anomalous-curve "
                                 "ECLP attack")
    ap.add_argument("--p", type=_int, required=False)
    ap.add_argument("--a", type=_int)
    ap.add_argument("--b", type=_int)
    ap.add_argument("--gx", type=_int)
    ap.add_argument("--gy", type=_int)
    ap.add_argument("--qx", type=_int)
    ap.add_argument("--qy", type=_int)
    ap.add_argument("--order", type=_int,
                    help="#E(F_p); attack needs order == p")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    need = ("p", "a", "b", "gx", "gy", "qx", "qy")
    if any(getattr(args, k) is None for k in need):
        ap.error("--p --a --b --gx --gy --qx --qy required")
    if args.order is not None and args.order != args.p:
        print(json.dumps({"ok": False,
                          "note": "#E = %d != p -- not anomalous; "
                                  "route to pohlig-hellman/bsgs"
                          % args.order}))
        return
    if args.order is None:
        print(json.dumps({"ok": False,
                          "note": "pass --order N after counting "
                                  "points; refusing to assume #E == p"}))
        return
    out = smart_dlog((args.gx, args.gy), (args.qx, args.qy),
                     args.p, args.a, args.b)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
