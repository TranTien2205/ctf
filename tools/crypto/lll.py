"""LLL lattice reduction. Uses fpylll when it is installed, otherwise a
pure-Python all-integer LLL so every lattice attack in this package still runs.

The pure path is Cohen's integral LLL (A Course in Computational Algebraic
Number Theory, Alg. 2.6.7): all arithmetic stays in Z by carrying the Gram
sub-determinants d[i] and the scaled coefficients lambda[i][j] = d[j+1]*mu[i][j].
No floats, so there is no precision ceiling on 1000-bit entries -- the cost is
speed, not correctness. Rough measured cost on this machine: a 21x21 lattice
with 130-bit entries reduces in about a second; a 61x61 lattice with 600-bit
entries is minutes. Install fpylll when a contest lattice gets large.
"""
from fractions import Fraction

try:                                    # optional, much faster when present
    from fpylll import IntegerMatrix as _IntegerMatrix, LLL as _fpLLL
    HAVE_FPYLLL = True
except Exception:                       # pragma: no cover - absent on this box
    HAVE_FPYLLL = False

__all__ = ["lll_reduce", "gram_schmidt", "is_lll_reduced", "backend", "HAVE_FPYLLL",
           "LAST_BACKEND"]

# Which path the most recent lll_reduce() actually took. Attacks report this so a
# run is never credited to fpylll when the pure-Python path did the work.
LAST_BACKEND = None


def backend(prefer_fpylll=True):
    return "fpylll" if (prefer_fpylll and HAVE_FPYLLL) else "pure-python"


def _fpylll_reduce(basis, delta):
    M = _IntegerMatrix(len(basis), len(basis[0]))
    for i, row in enumerate(basis):
        for j, v in enumerate(row):
            M[i, j] = int(v)
    _fpLLL.reduction(M, delta=delta)
    return [[M[i, j] for j in range(M.ncols)] for i in range(M.nrows)]


def _integral_lll(basis):
    """Cohen 2.6.7 with delta = 3/4. Raises _Dependent(k) on a dependent row."""
    n = len(basis)
    b = [None] + [list(row) for row in basis]          # 1-indexed
    d = [0] * (n + 2)
    d[0] = 1
    lam = [[0] * (n + 2) for _ in range(n + 2)]

    def dot(u, v):
        return sum(x * y for x, y in zip(u, v))

    d[1] = dot(b[1], b[1])
    if d[1] == 0:
        raise _Dependent(1)

    def red(k, l):
        if 2 * abs(lam[k][l]) <= d[l]:
            return
        q = _nearest_int(lam[k][l], d[l])
        b[k] = [x - q * y for x, y in zip(b[k], b[l])]
        lam[k][l] -= q * d[l]
        for i in range(1, l):
            lam[k][i] -= q * lam[l][i]

    def swap(k, kmax):
        b[k], b[k - 1] = b[k - 1], b[k]
        if k > 2:
            for j in range(1, k - 1):
                lam[k][j], lam[k - 1][j] = lam[k - 1][j], lam[k][j]
        lm = lam[k][k - 1]
        bb = (d[k - 2] * d[k] + lm * lm) // d[k - 1]
        for i in range(k + 1, kmax + 1):
            t = lam[i][k]
            lam[i][k] = (d[k] * lam[i][k - 1] - lm * t) // d[k - 1]
            lam[i][k - 1] = (bb * t + lm * lam[i][k]) // d[k]
        d[k - 1] = bb

    k, kmax = 2, 1
    while k <= n:
        if k > kmax:                                   # incremental Gram-Schmidt
            kmax = k
            for j in range(1, k + 1):
                u = dot(b[k], b[j])
                for i in range(1, j):
                    u = (d[i] * u - lam[k][i] * lam[j][i]) // d[i - 1]
                if j < k:
                    lam[k][j] = u
                else:
                    if u == 0:
                        raise _Dependent(k)
                    d[k] = u
        while True:
            red(k, k - 1)
            if 4 * d[k] * d[k - 2] < 3 * d[k - 1] * d[k - 1] - 4 * lam[k][k - 1] ** 2:
                swap(k, kmax)
                k = max(2, k - 1)
            else:
                for l in range(k - 2, 0, -1):
                    red(k, l)
                k += 1
                break
    return [b[i] for i in range(1, n + 1)]


class _Dependent(Exception):
    def __init__(self, k):
        super().__init__("row %d is dependent on the rows above it" % k)
        self.k = k


def _nearest_int(num, den):
    """Round num/den to the nearest integer, halves away from zero."""
    if den < 0:
        num, den = -num, -den
    q, r = divmod(num, den)
    if 2 * r >= den:
        q += 1
    return q


def lll_reduce(basis, delta=0.99, prefer_fpylll=True, drop_dependent=True):
    """LLL-reduce a list of integer row vectors; returns the new rows.

    Rows that turn out to be linearly dependent are dropped (fpylll returns them
    as zero rows; the pure path removes them and restarts), so the output can be
    shorter than the input. Zero rows are always removed from the input first.
    """
    global LAST_BACKEND
    rows = [[int(v) for v in row] for row in basis if any(row)]
    LAST_BACKEND = backend(prefer_fpylll)
    if not rows:
        return []
    width = max(len(r) for r in rows)
    rows = [r + [0] * (width - len(r)) for r in rows]
    if prefer_fpylll and HAVE_FPYLLL:
        out = _fpylll_reduce(rows, delta)
        return [r for r in out if any(r)]
    while True:
        try:
            out = _integral_lll(rows)
        except _Dependent as exc:
            if not drop_dependent or len(rows) <= 1:
                raise
            del rows[exc.k - 1]
            continue
        return [r for r in out if any(r)]


def gram_schmidt(basis):
    """Exact rational Gram-Schmidt: returns (mu, squared_norms)."""
    n = len(basis)
    star, norms = [], []
    mu = [[Fraction(0)] * n for _ in range(n)]
    for i in range(n):
        v = [Fraction(x) for x in basis[i]]
        for j in range(i):
            if norms[j] == 0:
                continue
            m = sum(Fraction(x) * y for x, y in zip(basis[i], star[j])) / norms[j]
            mu[i][j] = m
            if m:
                v = [a - m * c for a, c in zip(v, star[j])]
        star.append(v)
        norms.append(sum(x * x for x in v))
    return mu, norms


def is_lll_reduced(basis, delta=Fraction(3, 4)):
    """Check the two LLL conditions exactly. Used by the self-test, not by attacks."""
    mu, norms = gram_schmidt(basis)
    for i in range(len(basis)):
        for j in range(i):
            if abs(mu[i][j]) > Fraction(1, 2):
                return False, "size reduction fails at mu[%d][%d]=%s" % (i, j, mu[i][j])
    for i in range(1, len(basis)):
        if norms[i] < (Fraction(delta) - mu[i][i - 1] ** 2) * norms[i - 1]:
            return False, "Lovasz condition fails at index %d" % i
    return True, "reduced"
