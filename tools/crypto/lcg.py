"""Linear congruential generator recovery: plain, unknown-modulus, truncated."""
from math import gcd

from .numtheory import inverse
from .hnp import hnp_solve

__all__ = ["lcg_recover_params", "lcg_recover_modulus", "lcg_predict",
           "truncated_lcg_recover"]


def lcg_recover_params(outputs, modulus):
    """Recover (a, c) of x_{n+1} = a*x_n + c mod modulus from consecutive outputs.

    APPLICABILITY: you can see at least three CONSECUTIVE full states (not
    truncated, not hashed) and the modulus is known or guessable -- a power of
    two, or a named prime such as 2**127-1. Falsifier: the recovered (a, c) fail
    to reproduce the outputs you did not use.

    Returns {"a", "c", "modulus", "verified_on": k} or {"a": None, "reason": ...}.
    """
    xs = [int(v) % int(modulus) for v in outputs]
    m = int(modulus)
    if len(xs) < 3:
        return {"a": None, "reason": "need at least 3 consecutive outputs"}
    for i in range(len(xs) - 2):
        inv = inverse((xs[i + 1] - xs[i]) % m, m)
        if inv is None:
            continue                       # this difference is not invertible; slide
        a = (xs[i + 2] - xs[i + 1]) * inv % m
        c = (xs[i + 1] - a * xs[i]) % m
        if all((a * xs[j] + c) % m == xs[j + 1] for j in range(len(xs) - 1)):
            return {"a": a, "c": c, "modulus": m, "verified_on": len(xs) - 1,
                    "next": (a * xs[-1] + c) % m}
    return {"a": None, "reason": "no (a, c) reproduces the sequence for this modulus"}


def lcg_recover_modulus(outputs):
    """Recover the modulus too, from >= 6 consecutive full outputs.

    APPLICABILITY: consecutive full states, modulus unknown. Uses
    gcd over t_{i+2}*t_i - t_{i+1}^2 where t_i = x_{i+1} - x_i; each term is a
    multiple of the modulus.
    """
    xs = [int(v) for v in outputs]
    if len(xs) < 6:
        return {"modulus": None, "reason": "need at least 6 consecutive outputs"}
    t = [xs[i + 1] - xs[i] for i in range(len(xs) - 1)]
    g = 0
    for i in range(len(t) - 2):
        g = gcd(g, abs(t[i + 2] * t[i] - t[i + 1] * t[i + 1]))
    if g <= max(xs):
        return {"modulus": None, "reason": "gcd collapsed (%d); need more outputs" % g}
    # The gcd is a MULTIPLE of the modulus, often by a small factor (a factor of
    # 4 is common), so divide the small cofactors out and test each candidate.
    cands = [g]
    for f in range(2, 1001):
        if g % f == 0 and g // f > max(xs):
            cands.append(g // f)
    for cand in cands:
        got = lcg_recover_params(xs, cand)
        if got["a"] is not None:
            got["modulus_recovered"] = True
            return got
    return {"modulus": None, "reason": "gcd %d and its small cofactors gave no "
                                       "consistent (a, c)" % g}


def lcg_predict(state, a, c, modulus, count=1):
    """Forward-run the generator; also accepts a negative count to rewind."""
    out, x = [], int(state) % int(modulus)
    if count < 0:
        ainv = inverse(a, modulus)
        if ainv is None:
            raise ValueError("a is not invertible; cannot rewind")
        for _ in range(-count):
            x = (x - c) * ainv % modulus
            out.append(x)
        return out
    for _ in range(count):
        x = (a * x + c) % int(modulus)
        out.append(x)
    return out


def truncated_lcg_recover(highs, modulus, a, c, low_bits, prefer_fpylll=True):
    """Recover the discarded low bits when only the TOP bits of each state leak.

    APPLICABILITY: the generator publishes state >> low_bits (or state // 2**k),
    the parameters a, c and the modulus are known, and you hold several
    consecutive outputs. Needs roughly 2*log2(modulus)/(kept bits) samples.
    Falsifier: the recovered full state does not regenerate every published high
    part.

    highs: consecutive published values, each equal to state >> low_bits.
    Returns {"states": [...], "z0": int} or {"states": None, "reason": ...}.
    """
    m, a, c, k = int(modulus), int(a), int(c), int(low_bits)
    hs = [int(h) for h in highs]
    if len(hs) < 3:
        return {"states": None, "reason": "need at least 3 truncated outputs"}
    shift = 1 << k
    # z_i = A_i*z_0 + C_i mod m, with 0 <= z_i < 2**k
    A, C = 1, 0
    t_list, u_list = [A], [C]
    for i in range(len(hs) - 1):
        w = (a * hs[i] * shift + c - hs[i + 1] * shift) % m
        A = A * a % m
        C = (C * a + w) % m
        t_list.append(A)
        u_list.append(C)
    res = hnp_solve(t_list, u_list, m, shift, prefer_fpylll=prefer_fpylll)
    for z0 in [res["alpha"]] + res["candidates"] if res["alpha"] else res["candidates"]:
        if z0 is None:
            continue
        x = hs[0] * shift + z0
        states, ok = [x], True
        for i in range(1, len(hs)):
            x = (a * x + c) % m
            states.append(x)
            if x >> k != hs[i]:
                ok = False
                break
        if ok:
            return {"states": states, "z0": z0, "lattice_dim": res["lattice_dim"],
                    "next_state": (a * states[-1] + c) % m}
    return {"states": None, "reason": "lattice produced no consistent low bits",
            "candidates_checked": res["checked"], "lattice_dim": res["lattice_dim"]}
