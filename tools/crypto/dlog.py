"""Discrete logarithm: Pohlig-Hellman with automatic smoothness detection,
plus a plain baby-step giant-step for a single small group.
"""
from math import isqrt

from .numtheory import factorize, inverse, smoothness

__all__ = ["bsgs", "element_order", "pohlig_hellman", "dlog_report"]


def bsgs(g, h, p, order=None, max_table=1 << 22):
    """Baby-step giant-step in the multiplicative group mod p.

    APPLICABILITY: the group order is under roughly 2**44, so sqrt(order) table
    entries fit in memory. Above that you need Pohlig-Hellman on a smooth order.
    """
    p = int(p)
    n = int(order) if order else p - 1
    mstep = isqrt(n) + 1
    if mstep > max_table:
        return {"x": None, "reason": "sqrt(order) = %d exceeds the table limit" % mstep}
    table = {}
    cur = 1
    for j in range(mstep):
        table.setdefault(cur, j)
        cur = cur * g % p
    factor = pow(inverse(pow(g, mstep, p), p) or 1, 1, p)
    gamma = h % p
    for i in range(mstep + 1):
        if gamma in table:
            x = i * mstep + table[gamma]
            if pow(g, x, p) == h % p:
                return {"x": x % n, "steps": i}
        gamma = gamma * factor % p
    return {"x": None, "reason": "no logarithm found; h may be outside <g>"}


def element_order(g, p, order_factors=None):
    """Exact multiplicative order of g mod p, by peeling primes off p-1."""
    p = int(p)
    n = p - 1
    factors = order_factors or factorize(n)
    for q in factors:
        while n % q == 0 and pow(g, n // q, p) == 1:
            n //= q
    return n


def _dlog_prime_power(g, h, p, q, exp, order):
    """Digit-by-digit dlog in the subgroup of order q**exp (Pohlig-Hellman step)."""
    x = 0
    gamma = pow(g, order // q, p)                       # generator of the order-q part
    for k in range(exp):
        hk = pow(h * pow(inverse(pow(g, x, p), p), 1, p) % p, order // pow(q, k + 1), p)
        if q <= 1 << 20:
            cur, dk = 1, None
            for j in range(q):
                if cur == hk:
                    dk = j
                    break
                cur = cur * gamma % p
        else:
            got = bsgs(gamma, hk, p, order=q)
            dk = got["x"]
        if dk is None:
            return None
        x += dk * pow(q, k)
    return x


def pohlig_hellman(g, h, p, order=None, max_prime_bits=56):
    """Discrete log mod a prime p when the group order is smooth.

    APPLICABILITY: p-1 (or the order of g) factors into small primes -- check it
    with numtheory.smoothness first. Falsifier: the largest prime factor of the
    order is still large, in which case this is index calculus territory, not
    Pohlig-Hellman.

    The order of g itself is computed first, so a generator of a proper subgroup
    does not produce a coset representative that later fails to verify.
    """
    g, h, p = int(g), int(h), int(p)
    if pow(h, 1, p) == 1:
        return {"x": 0, "order": element_order(g, p)}
    base_factors = factorize(p - 1) if order is None else factorize(int(order))
    n = element_order(g, p, base_factors) if order is None else int(order)
    factors = factorize(n)
    largest = max(factors) if factors else 1
    if largest.bit_length() > max_prime_bits:
        return {"x": None, "order": n, "largest_prime_bits": largest.bit_length(),
                "reason": "largest prime factor of the order is %d bits: not smooth "
                          "enough for Pohlig-Hellman" % largest.bit_length()}
    residues, moduli = [], []
    for q, exp in sorted(factors.items()):
        xi = _dlog_prime_power(g, h, p, q, exp, n)
        if xi is None:
            return {"x": None, "order": n,
                    "reason": "no logarithm in the subgroup of order %d**%d; h is "
                              "probably not in <g>" % (q, exp)}
        residues.append(xi)
        moduli.append(pow(q, exp))
    from .numtheory import crt
    got = crt(residues, moduli)
    if got is None:
        return {"x": None, "order": n, "reason": "CRT inconsistent"}
    x = got[0] % n
    if pow(g, x, p) != h % p:
        return {"x": None, "order": n, "reason": "recovered x does not verify"}
    return {"x": x, "order": n, "order_factors": {str(k): v for k, v in factors.items()},
            "largest_prime": largest, "verified": True}


def dlog_report(p, g=None, h=None):
    """Smoothness triage before committing to a discrete-log attack."""
    rep = smoothness(int(p) - 1)
    rep["group"] = "Z_p^* with p of %d bits" % int(p).bit_length()
    if g is not None and h is not None:
        rep["solution"] = pohlig_hellman(g, h, p)
    return rep
