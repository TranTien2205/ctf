"""Hidden Number Problem lattice, and the two ECDSA nonce attacks built on it.

The HNP shape is: you know pairs (t_i, u_i) modulo m and you know that
(t_i * alpha + u_i) mod m is SMALL for every i. That single shape covers ECDSA
with short or biased nonces, truncated LCG output, and several "most significant
bits of a Diffie-Hellman secret" challenges.
"""
from .numtheory import inverse
from .lll import lll_reduce
from .ec import curve, ec_mul, pubkey_from_priv

__all__ = ["hnp_solve", "ecdsa_recover_biased_nonce", "ecdsa_recover_nonce_reuse",
           "required_signatures"]


def required_signatures(order_bits, nonce_bits):
    """Rough count of samples the lattice needs: leaked bits must exceed the secret."""
    leak = max(1, order_bits - nonce_bits)
    return max(3, int(2 * order_bits / leak))


def hnp_solve(t_list, u_list, modulus, bound, verify=None, prefer_fpylll=True):
    """Recover alpha from (t_i*alpha + u_i) mod modulus < bound for all i.

    APPLICABILITY: every sample leaks the same number of top bits of a value
    that is linear in one unknown - a short/biased ECDSA nonce, truncated LCG
    output, MSBs of a shared secret. You need roughly
    2*log2(modulus)/leaked_bits samples; below that the lattice has no
    unusually short vector and the attack cannot work at any m.

    Boneh-Venkatesan lattice, integer-scaled by `modulus` so no rationals are
    needed. `verify(alpha)` filters candidates; without it every candidate that
    satisfies the size condition is returned.

    Returns {"alpha": <int or None>, "candidates": [...], "checked": k}.
    """
    if len(t_list) != len(u_list):
        raise ValueError("t_list and u_list must have equal length")
    n, B, m = int(modulus), int(bound), len(t_list)
    if m < 2:
        raise ValueError("need at least two samples")
    half = B // 2
    dim = m + 2
    basis = [[0] * dim for _ in range(dim)]
    for i in range(m):
        basis[i][i] = n * n
    for i in range(m):
        basis[m][i] = (n * (t_list[i] % n)) % (n * n)
        basis[m + 1][i] = (n * ((u_list[i] - half) % n)) % (n * n)
    basis[m][m] = B
    basis[m + 1][m + 1] = n * B

    reduced = lll_reduce(basis, prefer_fpylll=prefer_fpylll)
    cands, seen = [], set()

    def offer(value):
        for v in (value % n, (-value) % n):
            if v and v not in seen:
                seen.add(v)
                cands.append(v)

    t0inv = inverse(t_list[0] % n, n)
    for row in reduced:
        cell = row[m]
        if cell and cell % B == 0:
            offer(cell // B)
        # second route: the first coordinate carries n*(k_0 - B/2); invert sample 0
        if t0inv is not None and row[0] % n == 0:
            k0 = row[0] // n + half
            if 0 <= k0 < B:
                offer((k0 - u_list[0]) * t0inv % n)

    def ok(alpha):
        return all(((t * alpha + u) % n) < B for t, u in zip(t_list, u_list))

    good = [c for c in cands if (verify(c) if verify else ok(c))]
    return {"alpha": good[0] if good else None, "candidates": good,
            "checked": len(cands), "lattice_dim": dim,
            "rows_after_reduction": len(reduced)}


def ecdsa_recover_biased_nonce(sigs, order, nonce_bits=None, nonce_bound=None,
                               curve_name=None, pubkey=None, prefer_fpylll=True):
    """Recover an ECDSA private key from signatures with short/biased nonces.

    APPLICABILITY: many signatures (roughly 2*order_bits/leaked_bits), all r
    values DISTINCT, and a stated or inferable bound on k -- "128-bit nonce" on a
    256-bit curve, or a timestamp-seeded k. If any two r repeat, use
    ecdsa_recover_nonce_reuse instead: it needs two signatures and no lattice.

    sigs: list of (r, s, z) with z the hash already reduced to an integer.
    Recovers d from k_i = s^-1 (z + d*r) mod order, 0 <= k_i < nonce_bound.
    """
    n = int(order)
    if nonce_bound is None:
        if nonce_bits is None:
            raise ValueError("supply nonce_bits or nonce_bound")
        nonce_bound = 1 << int(nonce_bits)
    t_list, u_list = [], []
    for (r, s, z) in sigs:
        sinv = inverse(int(s) % n, n)
        if sinv is None:
            raise ValueError("signature with non-invertible s")
        t_list.append(sinv * int(r) % n)
        u_list.append(sinv * int(z) % n)

    verify = None
    params = curve(curve_name) if curve_name else None
    if pubkey is not None and params is not None:
        target = (int(pubkey[0]), int(pubkey[1]))

        def verify(d):                                  # noqa: F811
            return pubkey_from_priv(d, params) == target

    out = hnp_solve(t_list, u_list, n, nonce_bound, verify=verify,
                    prefer_fpylll=prefer_fpylll)
    out["signatures_used"] = len(sigs)
    out["signatures_recommended"] = required_signatures(n.bit_length(),
                                                        nonce_bound.bit_length())
    out["pubkey_verified"] = bool(out["alpha"] is not None and verify is not None)
    out["private_key"] = out.pop("alpha")
    return out


def ecdsa_recover_nonce_reuse(sig_a, sig_b, order):
    """Recover d from two signatures that reused the same nonce (identical r).

    APPLICABILITY: two signatures share an r value. No lattice needed.
    sig_a, sig_b: (r, s, z).
    """
    n = int(order)
    r1, s1, z1 = (int(v) for v in sig_a)
    r2, s2, z2 = (int(v) for v in sig_b)
    if r1 % n != r2 % n:
        return {"private_key": None, "reason": "r values differ; nonce was not reused"}
    out = []
    for sign in (1, -1):
        den = inverse((s1 - sign * s2) % n, n)
        if den is None:
            continue
        k = (z1 - sign * z2) * den % n
        rinv = inverse(r1 % n, n)
        if rinv is None:
            continue
        d = (s1 * k - z1) * rinv % n
        if d:
            out.append({"nonce": k, "private_key": d, "s2_sign": sign})
    return {"private_key": out[0]["private_key"] if out else None, "solutions": out}
