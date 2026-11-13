#!/usr/bin/env python3
"""singular_ec.py -- ECDLP on a SINGULAR cubic, where the 'curve' is
not a real elliptic curve and the dlog collapses to easy algebra.

Challenge shape: an ECC handout whose discriminant is 0
(4a^3 + 27b^2 == 0 mod p). The singular point makes the group law
isomorphic to a field operation:

* cusp  y^2 = x^3              -> (F_p, +):  k = (x_Q/y_Q) * (x_P/y_P)^-1
* node  y^2 = x^2 (x + a)      -> (F_p*, *) via
     phi(x,y) = (y + alpha*x) / (y - alpha*x),  alpha^2 = a (mod p)
  when a is a quadratic residue. If a is a non-residue the target
  lives in F_{p^2}* -- this tool reports that honestly instead of
  building a quadratic-extension dlog.

    python3 tools/crypto/singular_ec.py --p P --a1 A --a0 B \
        --gx X --gy Y --qx X --qy Y

Coefficients are those of y^2 = x^3 + a2 x^2 + a1 x + a0; for the
usual short-Weierstrass handout pass --a1 a --a0 b.
    python3 tools/crypto/singular_ec.py --selftest

The falsifier is the discriminant check the tool runs FIRST: a
nonzero discriminant means a real elliptic curve -- route to
pohlig-hellman / bsgs / smart_attack, not here.
"""
import argparse
import json
import sys


def _dlog_multiplicative(g, h, p):
    """Trial + BSGS-lite dlog in F_p*; groups here are small in
    selftests and p-1 is smooth in the challenges this covers."""
    # simple BSGS, adequate up to ~2^40
    import math
    order = p - 1
    m = math.isqrt(order) + 1
    table = {}
    cur = 1
    for j in range(m):
        table[cur] = j
        cur = cur * g % p
    gm = pow(g, -m, p)
    cur = h
    for i in range(m + 1):
        if cur in table:
            return i * m + table[cur]
        cur = cur * gm % p
    return None


def singular_dlog(P, Q, p, a2, a1, a0):
    """Solve Q = k*P on the singular cubic
        y^2 = x^3 + a2 x^2 + a1 x + a0   over F_p.
    Detects cusp vs node itself; discriminant of the RHS cubic is
    the gate."""
    disc = (18 * a2 * a1 * a0 - 4 * a2 ** 3 * a0
            + a2 * a2 * a1 * a1 - 4 * a1 ** 3 - 27 * a0 * a0) % p
    if disc != 0:
        return {"ok": False, "disc_mod_p": disc,
                "note": "discriminant nonzero -- this IS an elliptic "
                        "curve; pohlig-hellman / bsgs / smart_attack "
                        "are the routes"}
    # singular means f has a double root r; gcd(f, f') finds it
    f = [a0 % p, a1 % p, a2 % p, 1]
    fp = [a1 % p, 2 * a2 % p, 3]
    # poly gcd over F_p
    def pmod(u, v):
        u = [c % p for c in u]
        while len(u) >= len(v) and u:
            k = u[-1] * pow(v[-1], -1, p) % p
            for j in range(len(v)):
                u[len(u) - len(v) + j] = (u[len(u) - len(v) + j]
                                          - k * v[j]) % p
            while u and u[-1] == 0:
                u.pop()
        return u
    g = f[:]
    v = fp[:]
    while v:
        g, v = v, pmod(g, v)
    # g monic: degree 1 -> double root -g[0]; degree 2 -> triple
    # root 0 (cusp x^3)
    if len(g) == 2:
        r = (-g[0]) % p
    elif len(g) == 3:
        r = 0
    else:
        return {"ok": False,
                "note": "unexpected gcd degree %d" % (len(g) - 1)}
    # shift x' = x - r puts the singular point at origin: curve is
    # y^2 = x'^2 (x' + s) where s = 3r + a2 (root-sum relation)
    s = (3 * r + a2) % p
    P2 = ((P[0] - r) % p, P[1] % p)
    Q2 = ((Q[0] - r) % p, Q[1] % p)
    if s % p == 0:
        # cusp: y^2 = x'^3 ; phi(x,y) = x/y is additive
        if P2[1] == 0 or Q2[1] == 0:
            return {"ok": False, "note": "point on the singularity"}
        tp = P2[0] * pow(P2[1], -1, p) % p
        tq = Q2[0] * pow(Q2[1], -1, p) % p
        k = tq * pow(tp, -1, p) % p
        return {"ok": True, "kind": "cusp (additive group)", "k": k}
    # node: y^2 = x'^2 (x' + s); alpha^2 = s
    alpha = None
    if pow(s, (p - 1) // 2, p) == 1:
        # Tonelli-Shanks (p small enough to brute-force too)
        alpha = _sqrt_mod(s, p)
    if alpha is None:
        return {"ok": False, "kind": "node over F_p^2",
                "note": "node slope alpha in F_p^2 -- multiplicative "
                        "dlog lives in the quadratic extension; not "
                        "implemented (documented boundary)"}
    def phi(pt):
        x, y = pt
        num = (y + alpha * x) % p
        den = (y - alpha * x) % p
        if den == 0:
            return None
        return num * pow(den, -1, p) % p
    g = phi(P2)
    h = phi(Q2)
    if g is None or h is None:
        return {"ok": False, "note": "point maps to node itself"}
    k = _dlog_multiplicative(g, h, p)
    if k is None:
        return {"ok": False, "note": "dlog in F_p* not found under "
                                     "BSGS bound -- order too large"}
    return {"ok": True, "kind": "node (multiplicative F_p*)", "k": k}


def _sqrt_mod(a, p):
    """Tonelli-Shanks."""
    if a % p == 0:
        return 0
    if pow(a, (p - 1) // 2, p) != 1:
        return None
    if p % 4 == 3:
        return pow(a, (p + 1) // 4, p)
    q, s = p - 1, 0
    while q % 2 == 0:
        q //= 2
        s += 1
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1
    c = pow(z, q, p)
    r = pow(a, (q + 1) // 2, p)
    t = pow(a, q, p)
    m = s
    while t != 1:
        i = 1
        tt = t * t % p
        while tt != 1:
            tt = tt * tt % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        r = r * b % p
        t = t * b * b % p
        c = b * b % p
        m = i
    return r


def _selftest():
    # cusp: y^2 = x^3 over F_101; phi=x/y additive. P=(2, ?) pick
    # real points on the curve first.
    p = 101
    pts = [(x, y) for x in range(p) for y in range(p)
           if y * y % p == x ** 3 % p and (x, y) != (0, 0)]
    P = pts[1]
    # k*P additive parameter t=x/y; k multiples -> t scales by k
    tp = P[0] * pow(P[1], -1, p) % p
    k_true = 42
    tq = tp * k_true % p
    # recover Q coordinates from tq: x/y = tq, y^2 = x^3 -> solve
    # x = tq^2 * w^2 ... parametrize: point (u^2, u^3) has t = 1/u,
    # so t = tq -> u = tq^-1 -> Q = (tq^-2, tq^-3)
    u = pow(tq, -1, p)
    Q = (u * u % p, u * u * u % p)
    out = singular_dlog(P, Q, p, 0, 0, 0)
    assert out.get("k") == k_true, (out, k_true)
    # node: y^2 = x^2(x + s), s=9 QR, F_101
    s = 9
    pts2 = [(x, y) for x in range(p) for y in range(p)
            if y * y % p == (x * x * (x + s)) % p and (x, y) != (0, 0)]
    Pn = pts2[3]
    # multiplicative map phi; pick k, compute Q by scaling phi
    alpha = _sqrt_mod(s, p)
    phi_p = (Pn[1] + alpha * Pn[0]) * pow((Pn[1] - alpha * Pn[0]) % p,
                                          -1, p) % p
    kn = 13
    phi_q = pow(phi_p, kn, p)
    # invert phi: u = (y+ax)/(y-ax) -> y(1-u) = -ax(1+u) ->
    # y = x*alpha*(u+1)/(u-1); then y^2 = x^2(x+s) gives x
    # x + s = (y/x)^2 = alpha^2 ((u+1)/(u-1))^2 -> x = s*(u-1)^2/
    #   (alpha^2 (u+1)^2 - (u-1)^2 ... solve numerically instead:
    Qn = None
    for x in range(1, p):
        num = (alpha * (phi_q + 1) * x) % p
        den = (phi_q - 1) % p
        if den == 0:
            continue
        y = num * pow(den, -1, p) % p
        if (y * y - x * x * (x + s)) % p == 0:
            Qn = (x, y)
            break
    assert Qn, "failed to materialize Q on the node"
    out2 = singular_dlog(Pn, Qn, p, s, 0, 0)
    assert out2.get("k") == kn, (out2, kn)
    # discriminant guard: a real curve must be refused
    bad = singular_dlog((0, 1), (0, 1), 101, 0, 0, 1)
    assert bad["ok"] is False and "elliptic" in bad["note"].lower() or \
        "real" in bad["note"].lower()
    print("singular_ec selftest: ok (cusp + node)")


def _int(s):
    return int(s, 0)


def main():
    ap = argparse.ArgumentParser(description="ECDLP on a singular "
                                 "cubic (cusp -> F_p+, node -> F_p*)")
    ap.add_argument("--p", type=_int)
    ap.add_argument("--a2", type=_int, default=0,
                    help="x^2 coefficient of y^2 = x^3 + a2 x^2 + "
                         "a1 x + a0")
    ap.add_argument("--a1", type=_int, default=0,
                    help="x coefficient (the 'a' in y^2 = x^3 + ax + b)")
    ap.add_argument("--a0", type=_int, default=0,
                    help="constant (the 'b' in y^2 = x^3 + ax + b)")
    ap.add_argument("--gx", type=_int)
    ap.add_argument("--gy", type=_int)
    ap.add_argument("--qx", type=_int)
    ap.add_argument("--qy", type=_int)
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()
    if args.selftest:
        _selftest()
        return
    need = ("p", "gx", "gy", "qx", "qy")
    if any(getattr(args, k) is None for k in need):
        ap.error("--p --gx --gy --qx --qy required "
                 "(--a2 --a1 --a0 default 0)")
    out = singular_dlog((args.gx, args.gy), (args.qx, args.qy),
                        args.p, args.a2 or 0, args.a1 or 0,
                        args.a0 or 0)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
