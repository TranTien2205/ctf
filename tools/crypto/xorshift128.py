#!/usr/bin/env python3
"""xorshift128.py -- state recovery for the classic xorshift128 PRNG.

xorshift128 (Marsaglia, 4x32-bit words) is PURE LINEAR over GF(2):
every output bit is a fixed XOR-subset of the 128 state bits. Four
consecutive outputs therefore give a 128x128 system, solvable by
Gaussian elimination with no SMT solver -- z3 is absent on this
box and not needed for this variant.

    python3 tools/crypto/xorshift128.py --outs 0x1a2b3c,0x4d5e6f,0x778899aa,0xbbccdd
    python3 tools/crypto/xorshift128.py --selftest

The tool reports the recovered initial state and verifies it by
regenerating the observed outputs, then predicts the next ones.

Honest boundary: xorshift128+ (V8 Math.random) and xoroshiro128+ add
their two 64-bit words with INTEGER addition -- the carry chain makes
output bits nonlinear over GF(2), so a pure linear solver cannot
recover them. Detected and reported, not guessed. For those, a SAT
solver on a box with z3 is the route.
"""
import argparse
import json
import sys

MASK128 = (1 << 128) - 1
M32 = 0xFFFFFFFF


def xs_step(state):
    """xorshift128 step; state = [s0,s1,s2,s3] of 32-bit values
    (integers for concrete run, or tuples-of-32-masks for symbolic)."""
    x = state[0]
    if isinstance(x, int):
        t = (x ^ ((x << 11) & M32)) & M32
        state[0], state[1], state[2] = state[1], state[2], state[3]
        w = state[3]
        state[3] = (w ^ (w >> 19) ^ t ^ (t >> 8)) & M32
    return state[3]


def _w_xor(a, b):
    return tuple(x ^ y for x, y in zip(a, b))


def _w_shl(a, n):
    return (0,) * n + tuple(a[:32 - n])


def _w_shr(a, n):
    return tuple(a[n:]) + (0,) * n


def symbolic_forms(noutputs):
    """Run the PRNG symbolically; each state/output bit is a GF(2)
    linear form over the 128 initial state bits, stored as a mask.
    Returns list of output words, each = tuple of 32 masks."""
    words = [[(1 << (i * 32 + j)) for j in range(32)]
             for i in range(4)]
    outs = []
    for _ in range(noutputs):
        t = _w_xor(words[0], _w_shl(words[0], 11))
        words[0], words[1], words[2] = words[1], words[2], words[3]
        w = words[3]
        words[3] = _w_xor(_w_xor(w, _w_shr(w, 19)),
                          _w_xor(t, _w_shr(t, 8)))
        outs.append(tuple(words[3]))
    return outs


def gf2_solve(equations):
    """equations: list of (mask, rhs). Gaussian elimination over
    GF(2); returns the solution vector as an int, or None if the
    system is underdetermined."""
    basis = {}
    for mask, rhs in equations:
        m, r = mask, rhs
        while m:
            p = m.bit_length() - 1
            if p not in basis:
                basis[p] = (m, r)
                break
            m ^= basis[p][0]
            r ^= basis[p][1]
        else:
            if r:
                return None                       # inconsistent
    if len(basis) < 128:
        return None                               # underdetermined
    sol = 0
    # pivot p = highest bit of m; every other set bit is < p, so
    # solve pivots in increasing order and lower bits are known
    for p, (m, r) in sorted(basis.items()):
        mm = m & ~(1 << p) & MASK128
        bit = r ^ ((mm & sol).bit_count() & 1)
        if bit:
            sol |= 1 << p
    return sol


def recover(outs):
    """outs: list of >=4 consecutive 32-bit outputs. Returns
    (initial_state[s0..s3], next_outputs) or raises."""
    forms = symbolic_forms(len(outs) + 4)
    equations = []
    for word_forms, word_val in zip(forms[:len(outs)], outs):
        for bit, mask in enumerate(word_forms):
            equations.append((mask, (word_val >> bit) & 1))
    sol = gf2_solve(equations)
    if sol is None:
        raise ValueError("could not recover state: outputs are not "
                         "from this linear system, or too few given")
    init = [(sol >> (i * 32)) & M32 for i in range(4)]
    st = list(init)
    check = [xs_step(st) for _ in range(len(outs))]
    if check != [o & M32 for o in outs]:
        raise ValueError("recovered state fails to reproduce the "
                         "given outputs -- wrong algorithm variant")
    nxt = [xs_step(st) for _ in range(4)]
    return init, nxt


def _selftest():
    init = [0xdeadbeef, 0x12345678, 0xcafebabe, 0x0badf00d]
    st = list(init)
    outs = [xs_step(st) for _ in range(6)]
    init2, nxt = recover(outs[:4])
    assert init2 == init, (init2, init)
    # outputs 4-6 = the next ones after the 4 given
    st2 = list(init)
    gen = [xs_step(st2) for _ in range(8)]
    assert nxt == gen[4:8], (nxt, gen[4:8])
    # wrong-variant rejection: 6 random outputs are almost surely NOT
    # on any xorshift128 orbit -- the overdetermined system or the
    # regeneration check must catch it
    import random
    random.seed(7)
    fake = [random.getrandbits(32) for _ in range(6)]
    try:
        recover(fake)
        raise AssertionError("fake outputs accepted")
    except ValueError:
        pass
    print("xorshift128 selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="recover xorshift128 "
                                 "state from consecutive outputs")
    ap.add_argument("--outs", help="comma-separated 32-bit outputs, "
                    "decimal or 0x-prefixed")
    ap.add_argument("--predict", type=int, default=4,
                    help="how many next outputs to print")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if not a.outs:
        ap.error("--outs required")
    outs = [int(x.strip(), 0) & M32 for x in a.outs.split(",")]
    try:
        init, nxt = recover(outs)
    except ValueError as exc:
        print(json.dumps({"ok": False, "error": str(exc),
                          "note": "xorshift128+ / xoroshiro128+ use "
                          "integer-addition output -- the carry chain "
                          "is nonlinear over GF(2) and needs a SAT "
                          "solver (z3), not this tool"}, indent=1))
        return 1
    print(json.dumps({"ok": True,
                      "initial_state": [hex(x) for x in init],
                      "next_outputs": [hex(x) for x in nxt][:a.predict],
                      "verified": True}, indent=1))


if __name__ == "__main__":
    raise SystemExit(main())
