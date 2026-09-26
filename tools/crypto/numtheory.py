"""Integer and modular helpers shared by every attack in this package.

Pure standard library. Nothing here calls random(): every "random" choice is a
deterministic search from a fixed start, so a self-test is reproducible.
"""
from math import gcd, isqrt

__all__ = [
    "integer_nth_root", "is_perfect_power", "crt", "inverse", "is_prime",
    "factorize", "factor_report", "is_smooth", "smoothness",
    "batch_gcd_shared_prime", "fermat_factor", "factor_from_d_or_phi",
    "eth_roots_mod_prime", "eth_root_mod_composite", "amm_root",
]


# --------------------------------------------------------------- roots / powers
def integer_nth_root(x, n):
    """Exact integer n-th root: return (root, is_exact) with root = floor(x**(1/n)).

    Newton iteration on integers only, so there is no float precision ceiling.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if x < 0:
        if n % 2 == 0:
            raise ValueError("even root of a negative number")
        r, exact = integer_nth_root(-x, n)
        return -r, exact
    if x in (0, 1):
        return x, True
    if n == 1:
        return x, True
    if n == 2:
        r = isqrt(x)
        return r, r * r == x
    r = 1 << ((x.bit_length() + n - 1) // n)
    while True:
        nxt = ((n - 1) * r + x // pow(r, n - 1)) // n
        if nxt >= r:
            break
        r = nxt
    while pow(r, n) > x:
        r -= 1
    while pow(r + 1, n) <= x:
        r += 1
    return r, pow(r, n) == x


def is_perfect_power(x, max_exp=64):
    """Return (base, exponent) if x == base**exponent with exponent >= 2, else None."""
    for e in range(2, max_exp + 1):
        if (1 << e) > x:
            break
        r, exact = integer_nth_root(x, e)
        if exact:
            return r, e
    return None


# --------------------------------------------------------------- modular basics
def inverse(a, m):
    """Modular inverse, or None when gcd(a, m) != 1 (never raises)."""
    try:
        return pow(a, -1, m)
    except ValueError:
        return None


def crt(residues, moduli):
    """Chinese remainder for possibly NON-coprime moduli.

    Returns (x, lcm) with x congruent to every residue, or None when the system
    is inconsistent. Coprime moduli are the common case (Hastad broadcast).
    """
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have equal length")
    x, m = 0, 1
    for r, n in zip(residues, moduli):
        if n <= 0:
            raise ValueError("moduli must be positive")
        g = gcd(m, n)
        if (r - x) % g != 0:
            return None
        lcm = m // g * n
        mg, ng = m // g, n // g
        inv = inverse(mg % ng, ng) if ng > 1 else 0
        t = ((r - x) // g % ng) * (inv or 0) % ng
        x = (x + m * t) % lcm
        m = lcm
    return x % m, m


# --------------------------------------------------------- primality / factoring
_MR_BASES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n):
    """Miller-Rabin over a fixed base set: deterministic below 3.3e24, else strong."""
    if n < 2:
        return False
    for p in _MR_BASES:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in _MR_BASES:
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def _pollard_brent(n, seed=1):
    """Brent's rho. Deterministic: the sequence constant walks 1,2,3,... upward."""
    if n % 2 == 0:
        return 2
    for c in range(seed, seed + 64):
        y, m, g, r, q = 2, 128, 1, 1, 1
        x = ys = y
        while g == 1:
            x = y
            for _ in range(r):
                y = (y * y + c) % n
            k = 0
            while k < r and g == 1:
                ys = y
                for _ in range(min(m, r - k)):
                    y = (y * y + c) % n
                    q = q * abs(x - y) % n
                g = gcd(q, n)
                k += m
            r *= 2
        if g == n:
            g = 1
            y = ys
            while g == 1:
                y = (y * y + c) % n
                g = gcd(abs(x - y), n)
        if 1 < g < n:
            return g
    return None


def factorize(n, trial_limit=100000, rho=True):
    """Full factorisation as {prime: exponent}. Trial division then Brent rho.

    Raises ValueError if a composite cofactor survives (so a caller never
    silently treats a composite as prime).
    """
    if n < 0:
        raise ValueError("n must be positive")
    out = {}
    if n in (0, 1):
        return out
    for p in [2] + list(range(3, trial_limit, 2)):
        if p * p > n:
            break
        while n % p == 0:
            out[p] = out.get(p, 0) + 1
            n //= p
    if n == 1:
        return out
    stack = [n]
    while stack:
        cur = stack.pop()
        if cur == 1:
            continue
        if is_prime(cur):
            out[cur] = out.get(cur, 0) + 1
            continue
        pp = is_perfect_power(cur)
        if pp:
            base, exp = pp
            stack.extend([base] * exp)
            continue
        if not rho:
            raise ValueError("composite cofactor left and rho disabled: %d" % cur)
        d = _pollard_brent(cur)
        if d is None:
            raise ValueError("could not factor cofactor %d" % cur)
        stack.extend([d, cur // d])
    return out


def factor_report(n, **kw):
    """Factorisation plus the numbers a triage decision actually needs."""
    f = factorize(n, **kw)
    largest = max(f) if f else 1
    return {
        "n_bits": n.bit_length(),
        "factors": {str(p): e for p, e in sorted(f.items())},
        "largest_prime": largest,
        "largest_prime_bits": largest.bit_length(),
        "distinct_primes": len(f),
    }


def is_smooth(n, bound, **kw):
    """True when every prime factor of n is <= bound."""
    try:
        f = factorize(n, **kw)
    except ValueError:
        return False
    return all(p <= bound for p in f)


def smoothness(n, **kw):
    """Smoothness verdict for a group order: is Pohlig-Hellman cheap here?

    APPLICABILITY: run it on p-1 (or the curve order) before committing to any
    discrete-log attack. largest_prime_bits <= ~40 means Pohlig-Hellman is cheap.
    """
    rep = factor_report(n, **kw)
    lb = rep["largest_prime_bits"]
    rep["pohlig_hellman"] = ("cheap" if lb <= 40 else
                             "feasible" if lb <= 56 else "too large")
    return rep


# ------------------------------------------------------- factoring shortcuts
def batch_gcd_shared_prime(moduli):
    """Find moduli that share a prime factor (bad RNG across many keys).

    APPLICABILITY: you hold several RSA moduli from the same generator, and no
    single one is factorable. Returns a list of {i, j, shared, factors}.
    """
    hits = []
    for i in range(len(moduli)):
        for j in range(i + 1, len(moduli)):
            g = gcd(moduli[i], moduli[j])
            if g > 1 and g not in (moduli[i], moduli[j]):
                hits.append({
                    "i": i, "j": j, "shared": g,
                    "factors": {str(i): [g, moduli[i] // g],
                                str(j): [g, moduli[j] // g]},
                })
    return hits


def fermat_factor(n, max_iters=1 << 22):
    """Factor n = p*q when p and q are close (|p-q| small).

    APPLICABILITY: the modulus was built from two primes generated by
    next_prime() from the same seed, so their high halves are identical.
    """
    if n % 2 == 0:
        return 2, n // 2
    a = isqrt(n)
    if a * a < n:
        a += 1
    for _ in range(max_iters):
        b2 = a * a - n
        b = isqrt(b2)
        if b * b == b2:
            p, q = a + b, a - b
            if p * q == n and q > 1:
                return int(p), int(q)
        a += 1
    return None


def factor_from_d_or_phi(n, e=None, d=None, phi=None):
    """Recover (p, q) from a leaked private exponent or phi(n)."""
    if phi is not None:
        s = n - phi + 1
        disc = s * s - 4 * n
        if disc < 0:
            return None
        r = isqrt(disc)
        if r * r != disc:
            return None
        p, q = (s + r) // 2, (s - r) // 2
        return (int(p), int(q)) if p * q == n else None
    if e is None or d is None:
        raise ValueError("supply phi, or both e and d")
    k = e * d - 1
    t = k
    while t % 2 == 0:
        t //= 2
        for g in (2, 3, 5, 7, 11, 13):
            x = pow(g, t, n)
            if x in (0, 1):
                continue
            y = gcd(x - 1, n)
            if 1 < y < n:
                return int(y), int(n // y)
    return None


# ------------------------------------------------------------- e-th roots mod p
def _order_r_dlog(base, target, r, p):
    """Brute-force dlog inside a subgroup of small prime order r."""
    if r > 1 << 22:
        return None
    cur = 1
    for j in range(r):
        if cur == target:
            return j
        cur = cur * base % p
    return None


def amm_root(c, r, p):
    """One r-th root of c mod p for PRIME r dividing p-1 (Adleman-Manders-Miller).

    Returns None when c is not an r-th residue. Deterministic: the non-residue
    is found by scanning 2,3,4,... instead of sampling.
    """
    c %= p
    if c == 0:
        return 0
    if (p - 1) % r != 0:
        inv = inverse(r, p - 1)
        return pow(c, inv, p) if inv is not None else None
    if pow(c, (p - 1) // r, p) != 1:
        return None
    s, t = p - 1, 0
    while s % r == 0:
        s //= r
        t += 1
    rho = 2
    while pow(rho, (p - 1) // r, p) == 1:
        rho += 1
        if rho > 1 << 20:
            return None
    k = 1
    while (k * s + 1) % r != 0:
        k += 1
    alpha = (k * s + 1) // r
    a = pow(rho, pow(r, t - 1) * s, p)
    b = pow(c, r * alpha - 1, p)
    cc = pow(rho, s, p)
    h = 1
    for i in range(1, t):
        d = pow(b, pow(r, t - 1 - i), p)
        j = 0 if d == 1 else _order_r_dlog(a, d, r, p)
        if j is None:
            return None
        j = (-j) % r
        b = b * pow(pow(cc, r, p), j, p) % p
        h = h * pow(cc, j, p) % p
        cc = pow(cc, r, p)
    root = pow(c, alpha, p) * h % p
    return root if pow(root, r, p) == c else None


def eth_roots_mod_prime(c, e, p, max_roots=4096):
    """ALL e-th roots of c modulo the prime p (e need not be coprime to p-1)."""
    c %= p
    if c == 0:
        return [0]
    roots = [c]
    for r, mult in sorted(factorize(e).items()):
        for _ in range(mult):
            nxt = []
            if (p - 1) % r == 0:
                units = [pow(g, (p - 1) // r, p) for g in range(2, 2 + 4 * r)]
                units = sorted({u for u in units if pow(u, r, p) == 1})
            else:
                units = [1]
            for val in roots:
                base = amm_root(val, r, p)
                if base is None:
                    continue
                for u in units:
                    cand = base * u % p
                    if pow(cand, r, p) == val:
                        nxt.append(cand)
            roots = sorted(set(nxt))[:max_roots]
            if not roots:
                return []
    return [x for x in roots if pow(x, e, p) == c]


def eth_root_mod_composite(c, e, factors, max_roots=4096):
    """All e-th roots of c mod n = prod(factors), the factorisation being known.

    APPLICABILITY: you already factored n (or the challenge handed you p and q)
    and gcd(e, phi) != 1, so the plain d = e^-1 mod phi does not exist.
    factors: list of DISTINCT primes.
    """
    if not factors:
        raise ValueError("need at least one prime factor")
    combos = [(0, 1)]
    for p in factors:
        local = eth_roots_mod_prime(c % p, e, p, max_roots=max_roots)
        if not local:
            return []
        nxt = []
        for x, m in combos:
            for r in local:
                res = crt([x, r], [m, p])
                if res:
                    nxt.append((res[0], res[1]))
        combos = nxt[:max_roots]
    n = 1
    for p in factors:
        n *= p
    return sorted({x % n for x, _ in combos if pow(x, e, n) == c % n})
