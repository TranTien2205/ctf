"""Integer polynomial helpers for the lattice attacks.

Univariate polys are coefficient lists, LOW degree first: [a0, a1, a2] is
a0 + a1*x + a2*x^2. Bivariate polys are dicts {(dx, dy): coeff}.

Everything here is pure Python. mpmath is used for numeric root isolation when
it is installed, with an exact integer bisection fallback that needs nothing.
"""
from fractions import Fraction
from math import gcd

try:
    import mpmath as _mpmath
    HAVE_MPMATH = True
except Exception:                       # pragma: no cover
    HAVE_MPMATH = False

__all__ = [
    "trim", "peval", "pmul", "padd", "pscale", "pdivmod_q", "poly_gcd",
    "bareiss_det", "resultant_univariate", "resultant_bivariate_x",
    "integer_roots", "bi_degree", "bi_eval_y", "HAVE_MPMATH",
]


# ------------------------------------------------------------------ univariate
def trim(p):
    q = list(p)
    while q and q[-1] == 0:
        q.pop()
    return q


def peval(p, x):
    acc = 0
    for c in reversed(p):
        acc = acc * x + c
    return acc


def padd(a, b):
    n = max(len(a), len(b))
    return trim([(a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)
                 for i in range(n)])


def pscale(a, k):
    return trim([c * k for c in a])


def pmul(a, b):
    if not a or not b:
        return []
    out = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    out[i + j] += ai * bj
    return trim(out)


def pdivmod_q(a, b):
    """Division over the rationals; returns (quotient, remainder) as Fractions."""
    b = trim(b)
    if not b:
        raise ZeroDivisionError("divide by the zero polynomial")
    r = [Fraction(c) for c in trim(a)]
    db, lead = len(b) - 1, Fraction(b[-1])
    q = [Fraction(0)] * max(0, len(r) - db)
    for i in range(len(r) - 1, db - 1, -1):
        if r[i] == 0:
            continue
        f = r[i] / lead
        q[i - db] = f
        for j in range(db + 1):
            r[i - db + j] -= f * b[j]
    while r and r[-1] == 0:
        r.pop()
    return q, r


def _primitive(p):
    """Clear denominators and the content, keeping the leading sign positive."""
    p = trim(p)
    if not p:
        return []
    den = 1
    for c in p:
        if isinstance(c, Fraction):
            den = den * c.denominator // gcd(den, c.denominator)
    ints = [int(Fraction(c) * den) for c in p]
    g = 0
    for c in ints:
        g = gcd(g, abs(c))
    if g > 1:
        ints = [c // g for c in ints]
    if ints and ints[-1] < 0:
        ints = [-c for c in ints]
    return ints


def poly_gcd(a, b):
    """GCD of two integer polynomials, returned primitive over Z."""
    a, b = trim(a), trim(b)
    while b:
        _, r = pdivmod_q(a, b)
        a, b = b, _primitive(r)
    return _primitive(a)


def bareiss_det(matrix):
    """Fraction-free integer determinant (exact, no floats)."""
    M = [[int(v) for v in row] for row in matrix]
    n = len(M)
    if n == 0:
        return 1
    sign, prev = 1, 1
    for k in range(n - 1):
        if M[k][k] == 0:
            for i in range(k + 1, n):
                if M[i][k] != 0:
                    M[k], M[i] = M[i], M[k]
                    sign = -sign
                    break
            else:
                return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                M[i][j] = (M[i][j] * M[k][k] - M[i][k] * M[k][j]) // prev
        prev = M[k][k]
    return sign * M[n - 1][n - 1]


def resultant_univariate(f, g):
    """Res(f, g) as the Sylvester determinant. Exact integers."""
    f, g = trim(f), trim(g)
    if not f or not g:
        return 0
    m, n = len(f) - 1, len(g) - 1
    if m == 0:
        return f[0] ** n
    if n == 0:
        return g[0] ** m
    size = m + n
    M = [[0] * size for _ in range(size)]
    for i in range(n):
        for j, c in enumerate(reversed(f)):
            M[i][i + j] = c
    for i in range(m):
        for j, c in enumerate(reversed(g)):
            M[n + i][i + j] = c
    return bareiss_det(M)


# ------------------------------------------------------------------- bivariate
def bi_degree(poly):
    dx = max((k[0] for k in poly), default=0)
    dy = max((k[1] for k in poly), default=0)
    return dx, dy


def bi_eval_y(poly, y0):
    """Substitute a concrete y, returning a univariate poly in x (low degree first)."""
    dx, _ = bi_degree(poly)
    out = [0] * (dx + 1)
    for (a, b), c in poly.items():
        if c:
            out[a] += c * pow(y0, b)
    return trim(out)


def resultant_bivariate_x(f, g):
    """Res_x(f, g) as a univariate polynomial in y, by evaluation + interpolation.

    This replaces sympy's resultant so Boneh-Durfee needs no third-party CAS.
    Degree bound: deg_x(f)*deg_y(g) + deg_x(g)*deg_y(f).
    """
    fx, fy = bi_degree(f)
    gx, gy = bi_degree(g)
    bound = fx * gy + gx * fy
    pts, vals = [], []
    y0, tried = 0, 0
    while len(pts) <= bound:
        tried += 1
        if tried > 40 * (bound + 2):
            raise ValueError("could not find enough specialisation points")
        fu, gu = bi_eval_y(f, y0), bi_eval_y(g, y0)
        # Specialising y is only valid where the x-degree does NOT drop: a
        # vanishing leading coefficient changes the Sylvester matrix size and
        # the interpolated polynomial would be wrong by a power of that
        # coefficient. Skip such points instead of poisoning the interpolation.
        if fu and gu and len(fu) - 1 == fx and len(gu) - 1 == gx:
            pts.append(y0)
            vals.append(resultant_univariate(fu, gu))
        y0 = -y0 + 1 if y0 <= 0 else -y0            # 0, 1, -1, 2, -2, ...
    return _interpolate(pts, vals)


def _interpolate(xs, ys):
    """Lagrange interpolation over Q, returned as an integer poly when it is one."""
    n = len(xs)
    acc = [Fraction(0)]
    for i in range(n):
        if ys[i] == 0:
            continue
        num, den = [Fraction(1)], Fraction(1)
        for j in range(n):
            if i == j:
                continue
            num = pmul(num, [Fraction(-xs[j]), Fraction(1)])
            den *= Fraction(xs[i] - xs[j])
        term = [c * Fraction(ys[i]) / den for c in num]
        acc = padd(acc, term)
    out = trim(acc)
    if all(Fraction(c).denominator == 1 for c in out):
        return [int(c) for c in out]
    return out


# --------------------------------------------------------------- integer roots
def integer_roots(coeffs, bound=None, dps=120):
    """Every integer root x0 of the polynomial with |x0| <= bound.

    Primary path: mpmath.polyroots (high precision, what the original TYPHON
    solver used). Fallback: exact sign-change bracketing plus integer bisection,
    which needs only the standard library.
    """
    p = trim([int(c) for c in coeffs])
    if not p:
        return []
    if bound is None:
        bound = 1 << 256
    cands = set()
    if p[0] == 0:
        cands.add(0)
    if HAVE_MPMATH and len(p) > 1:
        cands |= set(_mpmath_candidates(p, bound, dps))
    cands |= set(_bisect_candidates(p, bound))
    return sorted(c for c in cands if abs(c) <= bound and peval(p, c) == 0)


def _mpmath_candidates(p, bound, dps):
    hi = list(reversed(p))                      # mpmath wants highest degree first
    _mpmath.mp.dps = dps
    try:
        roots = _mpmath.polyroots([_mpmath.mpf(int(c)) for c in hi],
                                  maxsteps=500, extraprec=4 * dps)
    except Exception:
        return []
    out = []
    for rt in roots:
        if abs(_mpmath.im(rt)) > _mpmath.mpf(10) ** (-dps // 3):
            continue
        xi = int(_mpmath.nint(_mpmath.re(rt)))
        out.extend(c for c in (xi - 1, xi, xi + 1) if abs(c) <= bound + 2)
    return out


def _bisect_candidates(p, bound):
    """Bracket sign changes on a geometric grid, then bisect over the integers."""
    grid = [0]
    k = 0
    while (1 << k) <= bound:
        grid.append(1 << k)
        grid.append(-(1 << k))
        k += 1
    grid.extend([bound, -bound])
    grid = sorted(set(x for x in grid if abs(x) <= bound))
    out = []
    for lo, hi in zip(grid, grid[1:]):
        flo, fhi = peval(p, lo), peval(p, hi)
        if flo == 0:
            out.append(lo)
        if fhi == 0:
            out.append(hi)
        if flo == 0 or fhi == 0 or (flo > 0) == (fhi > 0):
            continue
        while hi - lo > 1:
            mid = (lo + hi) // 2
            fm = peval(p, mid)
            if fm == 0:
                out.append(mid)
                break
            if (fm > 0) == (flo > 0):
                lo, flo = mid, fm
            else:
                hi, fhi = mid, fm
        else:
            out.extend([lo, hi])
    return out
