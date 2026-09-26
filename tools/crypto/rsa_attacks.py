"""RSA attacks: broadcast, small exponent, common modulus, Wiener, Boneh-Durfee,
Coppersmith with known high bits of a factor, and the cheap factorisations.

The lattice attacks here run on this package's own pure-Python LLL, so nothing
in this file needs fpylll, sympy or pycryptodome. fpylll is used automatically
when it happens to be installed, and it is much faster at contest sizes.
"""
from math import gcd, isqrt

from .numtheory import (integer_nth_root, crt, inverse, fermat_factor,
                        batch_gcd_shared_prime, factor_from_d_or_phi)
from .lll import lll_reduce
from .polynomials import (pmul, resultant_bivariate_x, poly_gcd, integer_roots,
                          bi_degree)

__all__ = ["hastad_broadcast", "small_e_root", "common_modulus", "wiener",
           "boneh_durfee", "boneh_durfee_escalate", "coppersmith_high_bits", "factor_with_known_high_bits",
           "pollard_pm1", "fermat_factor", "batch_gcd_shared_prime",
           "factor_from_d_or_phi", "rsa_decrypt_with_factors"]


# ------------------------------------------------------------------- broadcast
def hastad_broadcast(pairs, e=3, message_bytes=None):
    """Hastad broadcast: the same message under a small e to several moduli.

    APPLICABILITY: at least e ciphertexts of the SAME plaintext, each under a
    different modulus, with a small public exponent and no per-recipient padding.
    Falsifier: the CRT combination is not an exact e-th power -- then the
    messages were padded differently and this plain form cannot work.

    pairs: [(n1, c1), (n2, c2), ...]. Returns
    {"message": int, "bytes": hex, "moduli_used": k} or {"message": None, ...}.
    """
    e = int(e)
    pairs = [(int(n), int(c)) for n, c in pairs]
    if len(pairs) < e:
        return {"message": None,
                "reason": "need at least e=%d ciphertexts, got %d" % (e, len(pairs))}
    for i in range(len(pairs)):
        for j in range(i + 1, len(pairs)):
            g = gcd(pairs[i][0], pairs[j][0])
            if g > 1:
                return {"message": None,
                        "reason": "moduli %d and %d share a factor %d -- factor them "
                                  "directly instead" % (i, j, g)}
    combined = crt([c for _, c in pairs], [n for n, _ in pairs])
    if combined is None:
        return {"message": None, "reason": "CRT inconsistent"}
    value, modulus = combined
    root, exact = integer_nth_root(value, e)
    if not exact:
        return {"message": None, "modulus_bits": modulus.bit_length(),
                "reason": "CRT result is not an exact %d-th power: the plaintext is "
                          "padded, or e is wrong" % e}
    return {"message": root, "hex": "%x" % root,
            "bytes": _to_bytes(root, message_bytes),
            "moduli_used": len(pairs), "e": e}


def _to_bytes(value, length=None):
    if length is None:
        length = (value.bit_length() + 7) // 8 or 1
    try:
        return value.to_bytes(int(length), "big").hex()
    except OverflowError:
        return "%x" % value


def small_e_root(n, e, c, max_k=1 << 16, message_bytes=None):
    """Plain e-th root of c over the integers, sweeping c + k*n.

    APPLICABILITY: one modulus, small e, and a short message, so m**e did not
    wrap the modulus (or wrapped only a few times). Falsifier: no k below the
    sweep limit makes c + k*n an exact e-th power.
    """
    n, e, c = int(n), int(e), int(c)
    for k in range(int(max_k)):
        root, exact = integer_nth_root(c + k * n, e)
        if exact:
            return {"message": root, "k": k, "hex": "%x" % root,
                    "bytes": _to_bytes(root, message_bytes)}
    return {"message": None, "reason": "no exact root for k < %d" % max_k}


def common_modulus(n, e1, c1, e2, c2, message_bytes=None):
    """One modulus, two exponents, same message.

    APPLICABILITY: gcd(e1, e2) == 1. Falsifier: the exponents share a factor,
    which is the gcd(e, phi) > 1 shape instead.
    """
    n, e1, e2, c1, c2 = int(n), int(e1), int(e2), int(c1), int(c2)
    g = gcd(e1, e2)
    if g != 1:
        return {"message": None, "reason": "gcd(e1, e2) = %d != 1" % g}
    old_r, r = e1, e2
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    a, b = old_s, old_t
    x = c1 if a >= 0 else inverse(c1, n)
    y = c2 if b >= 0 else inverse(c2, n)
    if x is None or y is None:
        return {"message": None, "reason": "a ciphertext is not invertible mod n"}
    m = pow(x, abs(a), n) * pow(y, abs(b), n) % n
    return {"message": m, "hex": "%x" % m, "bytes": _to_bytes(m, message_bytes)}


# ---------------------------------------------------------------------- Wiener
def _cf(a, b):
    while b:
        q = a // b
        yield q
        a, b = b, a - q * b


def _convergents(cf):
    h0, h1, k0, k1 = 0, 1, 1, 0
    for q in cf:
        h0, h1 = h1, q * h1 + h0
        k0, k1 = k1, q * k1 + k0
        yield h1, k1


def wiener(n, e):
    """Wiener continued-fraction attack: recover a SMALL private exponent.

    APPLICABILITY: d < n**0.25, which shows up as an e of the same magnitude as
    n (a big, random-looking public exponent). Falsifier: the convergents run
    out with no d that makes p+q a perfect square discriminant -- then try
    boneh_durfee, which reaches d < n**0.292.
    """
    n, e = int(n), int(e)
    for k, d in _convergents(_cf(e, n)):
        if k == 0 or (e * d - 1) % k != 0:
            continue
        phi = (e * d - 1) // k
        b = n - phi + 1
        disc = b * b - 4 * n
        if disc < 0:
            continue
        s = isqrt(disc)
        if s * s == disc and (b + s) % 2 == 0:
            p, q = (b + s) // 2, (b - s) // 2
            if p * q == n:
                return {"d": d, "p": int(p), "q": int(q), "d_bits": d.bit_length()}
            return {"d": d, "p": None, "q": None, "d_bits": d.bit_length()}
    return {"d": None, "reason": "no convergent yields a valid d (d >= n**0.25); "
                                 "escalate to boneh_durfee"}


# ---------------------------------------------------------------- Boneh-Durfee
def _bd_polys(m, t, A):
    """x-shifts plus helpful y-shifts of f(x,y) = x*(A+y) + 1 mod e."""
    def mul(P, Q):
        R = {}
        for (a, b), c in P.items():
            for (d, e2), f2 in Q.items():
                key = (a + d, b + e2)
                R[key] = R.get(key, 0) + c * f2
        return R
    f = {(1, 0): A, (1, 1): 1, (0, 0): 1}
    fpows = [{(0, 0): 1}]
    for _ in range(m):
        fpows.append(mul(fpows[-1], f))
    polys = []
    for k in range(m + 1):
        for i in range(m - k + 1):
            polys.append((k, {(dx + i, dy): c for (dx, dy), c in fpows[k].items()}))
    step = (m // t) if t > 0 else m + 1
    for j in range(1, t + 1):
        for k in range(step * j, m + 1):
            polys.append((k, {(dx, dy + j): c for (dx, dy), c in fpows[k].items()}))
    return polys


def boneh_durfee(n, e, delta=0.28, m=6, t=None, prefer_fpylll=True, try_wiener=True):
    """Boneh-Durfee: recover a small private exponent up to d < n**0.292.

    APPLICABILITY: the challenge states a bound like "d < n^0.27", or Wiener
    already failed while e is still large. Falsifier: LLL at m = 6..8 yields no
    bivariate relation whose root gives p+q -- then d is genuinely above the
    0.292 bound and no lattice parameter fixes it.

    Lattice: f(x,y) = x*(A+y) + 1 == 0 mod e with A = n+1 and the root
    (k, -(p+q)). Cost grows fast with m; with the pure-Python LLL keep m small
    (measured: m=4 on a 128-bit modulus is about a second, m=6 on 512 bits is
    impractical -- install fpylll for contest sizes).

    Returns {"p", "q", "d", "m", "t"} or {"p": None, "reason": ...}.
    """
    n, e = int(n), int(e)
    if try_wiener:
        w = wiener(n, e)
        if w.get("p"):
            w.update({"m": None, "t": None, "note": "Wiener sufficed; no lattice needed"})
            return w
    if t is None:
        t = max(1, int((1 - 2 * delta) * m + 0.5))
    X = 1 << (int(delta * n.bit_length()) + 1)            # ~ 2*n**delta, no floats
    Y = 3 * isqrt(n) + 1                                  # bound on p+q
    A = n + 1
    polys = _bd_polys(m, t, A)
    monoms = sorted({mon for _, P in polys for mon in P})
    col = {mon: i for i, mon in enumerate(monoms)}
    basis = [[0] * len(monoms) for _ in polys]
    for r, (k, P) in enumerate(polys):
        emul = pow(e, m - k)
        for (dx, dy), c in P.items():
            basis[r][col[(dx, dy)]] = c * emul * pow(X, dx) * pow(Y, dy)
    reduced = lll_reduce(basis, prefer_fpylll=prefer_fpylll)

    def row_to_poly(row):
        out = {}
        for idx, mon in enumerate(monoms):
            v = row[idx]
            if v:
                dx, dy = mon
                out[mon] = v // (pow(X, dx) * pow(Y, dy))
        return {k2: v for k2, v in out.items() if v}

    def try_s(s):
        s = int(s)
        disc = s * s - 4 * n
        if disc < 0:
            return None
        sq = isqrt(disc)
        if sq * sq != disc:
            return None
        p, q = (s + sq) // 2, (s - sq) // 2
        return (int(p), int(q)) if p * q == n and p > 1 and q > 1 else None

    def finish(pq):
        p, q = pq
        d = inverse(e, (p - 1) * (q - 1))
        return {"p": p, "q": q, "d": d, "m": m, "t": t,
                "lattice_dim": len(basis), "delta": delta}

    usable = []
    for row in reduced:
        P = row_to_poly(row)
        if not P:
            continue
        dx, dy = bi_degree(P)
        if dx == 0 and dy >= 1:                      # already a polynomial in y only
            coeffs = [0] * (dy + 1)
            for (_, b), c in P.items():
                coeffs[b] = c
            for root in integer_roots(coeffs, bound=Y):
                got = try_s(-root)
                if got:
                    return finish(got)
        elif dx >= 1 and dy >= 1:
            usable.append(P)
        if len(usable) >= 6:
            break
    if len(usable) < 2:
        return {"p": None, "reason": "no usable bivariate row after reduction; raise m",
                "m": m, "t": t, "lattice_dim": len(basis)}

    # A vanishing resultant means the two rows share a factor, which happens
    # often; try every pair of the shortest rows rather than giving up on the
    # first empty one.
    res_polys = []
    for a in range(len(usable)):
        for b in range(a + 1, len(usable)):
            R = resultant_bivariate_x(usable[a], usable[b])
            if len(R) > 1:
                res_polys.append(R)
            if len(res_polys) >= 3:
                break
        if len(res_polys) >= 3:
            break
    if not res_polys:
        return {"p": None, "reason": "every resultant vanished (rows share a factor); "
                                     "raise m", "m": m, "t": t,
                "lattice_dim": len(basis), "usable_rows": len(usable)}
    cand_polys = list(res_polys)
    for a in range(len(res_polys)):
        for b in range(a + 1, len(res_polys)):
            g = poly_gcd(res_polys[a], res_polys[b])
            if len(g) >= 2:
                cand_polys.insert(0, g)
    for poly in cand_polys:
        if len(poly) == 2:                            # linear: y = -c0/c1
            c0, c1 = poly[0], poly[1]
            if c1 and c0 % c1 == 0:
                got = try_s(-(-c0 // c1))
                if got:
                    return finish(got)
            approx = -round(c0 / c1) if c1 else 0
            for cand in (approx - 1, approx, approx + 1):
                got = try_s(-cand)
                if got:
                    return finish(got)
        else:
            for root in integer_roots(poly, bound=Y):
                got = try_s(-root)
                if got:
                    return finish(got)
    return {"p": None, "reason": "roots found no valid p+q; raise m or delta",
            "m": m, "t": t, "lattice_dim": len(basis)}


# --------------------------------------------------------------- Coppersmith
def boneh_durfee_escalate(n, e, delta=0.28, m_list=(6, 7, 8, 9, 10), **kw):
    """Run boneh_durfee over increasing lattice parameters, as a contest would.

    APPLICABILITY: identical to boneh_durfee; use this when you do not want to
    pick m by hand. Each attempt is reported so a failure is still informative.
    """
    attempts = []
    for m in m_list:
        got = boneh_durfee(n, e, delta=delta, m=int(m), **kw)
        attempts.append({"m": int(m), "found": bool(got.get("p")),
                         "reason": got.get("reason")})
        if got.get("p"):
            got["attempts"] = attempts
            return got
        kw["try_wiener"] = False              # only worth trying once
    return {"p": None, "reason": "no lattice parameter in %s worked" % (list(m_list),),
            "attempts": attempts}


def coppersmith_high_bits(n, a, X, m=8, t=None, prefer_fpylll=True):
    """Small-root core: find |x0| <= X with gcd(n, a + x0) a nontrivial factor.

    APPLICABILITY: you know an approximation `a` of a factor of n to within X.
    Pass the CENTRED guess so |x0| is minimised -- that one bit of slack is what
    brings the exactly-half-known case inside the finite-lattice bound.
    Falsifier: X exceeds about n**0.25 for a two-prime modulus; no m fixes that.
    """
    n, a, X = int(n), int(a), int(X)
    if t is None:
        t = m
    f = [a % n, 1]
    fpows = [[1]]
    for _ in range(m + t):
        fpows.append(pmul(fpows[-1], f))
    rows = [[c * pow(n, m - i) for c in fpows[i]] for i in range(m + 1)]
    fm = fpows[m]
    for i in range(1, t + 1):
        rows.append([0] * i + list(fm))
    dim = max(len(r) for r in rows)
    basis = [[(row[j] if j < len(row) else 0) * pow(X, j) for j in range(dim)]
             for row in rows]
    reduced = lll_reduce(basis, prefer_fpylll=prefer_fpylll)

    polys = []
    for row in reduced[:8]:
        co = [row[j] // pow(X, j) for j in range(dim)]
        if any(co):
            polys.append(co)

    def check(x0):
        if abs(x0) > X + 2:
            return None
        g = gcd(a + x0, n)
        return g if 1 < g < n else None

    for poly in polys:                                # textbook route: shortest row
        for x0 in integer_roots(poly, bound=X):
            g = check(x0)
            if g:
                return {"factor": g, "cofactor": n // g, "x0": x0,
                        "m": m, "t": t, "route": "row-root", "lattice_dim": dim}
    for i in range(len(polys)):                       # boundary route: pairwise GCD
        for j in range(i + 1, len(polys)):
            g = poly_gcd(polys[i], polys[j])
            if 1 <= len(g) - 1 <= 4:
                for x0 in integer_roots(g, bound=X):
                    f2 = check(x0)
                    if f2:
                        return {"factor": f2, "cofactor": n // f2, "x0": x0,
                                "m": m, "t": t, "route": "poly-gcd", "lattice_dim": dim}
    return {"factor": None, "reason": "no small root; raise m (and t) or supply more "
                                      "known bits", "m": m, "t": t, "lattice_dim": dim}


def factor_with_known_high_bits(n, known, known_bits, p_bits, m=8, t=None,
                                prefer_fpylll=True):
    """Factor n when the TOP `known_bits` of a `p_bits`-long prime are known.

    APPLICABILITY: the handout leaks the high half of p (a printed prefix, a
    partially redacted key, a seeded prime). The unknown part must be at most
    about a quarter of the bits of n. Falsifier: fewer than half the bits of p
    are known -- no lattice parameter recovers that.

    known: the leaked value, i.e. p >> (p_bits - known_bits).
    """
    n, known = int(n), int(known)
    unknown = int(p_bits) - int(known_bits)
    if unknown <= 0:
        p = known
        return ({"factor": p, "cofactor": n // p, "x0": 0, "route": "no unknown bits"}
                if n % p == 0 else {"factor": None, "reason": "known value is not a factor"})
    a = (known << unknown) + (1 << (unknown - 1))      # centre the unknown
    X = 1 << (unknown - 1)
    out = coppersmith_high_bits(n, a, X, m=m, t=t, prefer_fpylll=prefer_fpylll)
    if out.get("factor"):
        p = out["factor"]
        if (p >> unknown) != known and (n // p) >> unknown == known:
            p, out["cofactor"] = n // p, p
            out["factor"] = p
        out["unknown_bits"] = unknown
        out["prefix_matches"] = (p >> unknown) == known
    else:
        out["unknown_bits"] = unknown
    return out


# ------------------------------------------------------------ cheap factorings
def pollard_pm1(n, b1=100000):
    """Pollard p-1: factor n when some p-1 is B-smooth.

    APPLICABILITY: a "weak prime" hint, or a modulus that resists everything
    else cheaply. Falsifier: the bound reaches 10**7 with no factor.
    """
    n = int(n)
    a = 2
    for j in range(2, int(b1) + 1):
        a = pow(a, j, n)
        if j % 128 == 0 or j == b1:
            g = gcd(a - 1, n)
            if 1 < g < n:
                return {"factor": g, "cofactor": n // g, "bound_reached": j}
            if g == n:
                return {"factor": None, "reason": "gcd collapsed to n at j=%d; "
                                                  "restart with a smaller bound" % j}
    return {"factor": None, "reason": "no factor with B1 = %d" % b1}


def rsa_decrypt_with_factors(n, e, c, p, q=None):
    """Finish the job once a factor is known; handles gcd(e, phi) > 1 too."""
    n, e, c, p = int(n), int(e), int(c), int(p)
    q = int(q) if q else n // p
    phi = (p - 1) * (q - 1)
    d = inverse(e, phi)
    if d is not None:
        m = pow(c, d, n)
        return {"message": m, "hex": "%x" % m, "d": d}
    from .numtheory import eth_root_mod_composite
    roots = eth_root_mod_composite(c, e, [p, q])
    return {"message": roots[0] if roots else None, "roots": roots,
            "note": "gcd(e, phi) > 1: several roots, pick the printable one"}
