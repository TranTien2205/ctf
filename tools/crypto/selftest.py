#!/usr/bin/env python3
"""Deterministic self-test for every attack in tools/crypto.

Each test builds a small instance with a FIXED seed, runs the attack, and
asserts the recovered value equals the planted secret. No network, no fpylll, no
sympy, no pycryptodome: if this passes, the package works on a bare Python.

    python3 tools/crypto/selftest.py            # fast set
    python3 tools/crypto/selftest.py --slow     # plus the large lattice cases
    python3 tools/crypto/selftest.py --json
    python3 tools/crypto/selftest.py --only wiener,hastad
"""
import argparse
import hashlib
import json
import os
import random
import sys
import time

if __package__ in (None, ""):                  # allow running the file directly
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from crypto import (numtheory as nt, lll, polynomials as poly, lcg, lfsr, dlog,
                        hash_ext, rsa_attacks as rsa, hnp, ec, mt19937, xor)
else:                                          # pragma: no cover
    from . import (numtheory as nt, lll, polynomials as poly, lcg, lfsr, dlog,
                   hash_ext, rsa_attacks as rsa, hnp, ec, mt19937, xor)

SEED = 20260925
TESTS = []

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TYPHON = os.path.join(ROOT, "CSCV2026", "Crypto", "solve", "output_typhon.txt")


class Skip(Exception):
    """A test needs an artifact or an optional library that is absent here.

    Not a pass: the module docstring promises this file runs on a bare Python, so
    the one test that needs a real handout and pycryptodome reports skipped
    rather than quietly counting as proof.
    """


def test(name, slow=False):
    def wrap(fn):
        TESTS.append((name, fn, slow))
        return fn
    return wrap


def rng(salt=0):
    """A fresh generator with a fixed seed, so every test is reproducible."""
    return random.Random(SEED + salt)


def gen_prime(bits, r):
    while True:
        cand = r.getrandbits(bits) | (1 << (bits - 1)) | 1
        if nt.is_prime(cand):
            return cand


def smooth_prime(min_bits, r, max_factor=200):
    """A prime p with p-1 built only from primes below max_factor."""
    smalls = [q for q in range(2, max_factor) if nt.is_prime(q)]
    while True:
        v = 2
        while v.bit_length() < min_bits - 8:
            v *= r.choice(smalls)
        for mult in smalls:
            cand = v * mult + 1
            if cand.bit_length() >= min_bits - 6 and nt.is_prime(cand):
                return cand


# --------------------------------------------------------------------- helpers
@test("helpers")
def t_helpers():
    r = rng(1)
    assert nt.integer_nth_root(pow(7, 31), 31) == (7, True)
    assert nt.integer_nth_root(pow(10, 40) + 1, 3)[1] is False
    assert nt.crt([2, 3, 2], [3, 5, 7]) == (23, 105)
    assert nt.crt([1, 3], [4, 6]) == (9, 12)              # non-coprime moduli
    assert nt.inverse(4, 8) is None
    p, q = gen_prime(96, r), gen_prime(96, r)
    shared = gen_prime(96, r)
    hits = nt.batch_gcd_shared_prime([p * shared, q * shared, p * q])
    assert hits and hits[0]["shared"] == shared, "batch gcd missed the shared prime"
    p2 = gen_prime(128, r)
    q2 = p2 + 2
    while not nt.is_prime(q2):
        q2 += 2
    assert sorted(nt.fermat_factor(p2 * q2)) == sorted([p2, q2])
    e, n = 3, 101 * 103 * 107
    msg = 12345
    roots = nt.eth_root_mod_composite(pow(msg, e, n), e, [101, 103, 107])
    assert msg in roots, "e-th root mod composite lost the plaintext"
    d = r.getrandbits(64) | 1
    p3, q3 = gen_prime(64, r), gen_prime(64, r)
    phi = (p3 - 1) * (q3 - 1)
    assert sorted(nt.factor_from_d_or_phi(p3 * q3, phi=phi)) == sorted([p3, q3])
    return {"checks": 9}


@test("lll")
def t_lll():
    r = rng(2)
    dim = 12
    basis = [[r.getrandbits(80) for _ in range(dim)] for _ in range(dim)]
    reduced = lll.lll_reduce(basis, prefer_fpylll=False)
    ok, why = lll.is_lll_reduced(reduced)
    assert ok, why

    def gram_det(rows):
        return poly.bareiss_det([[sum(x * y for x, y in zip(u, v)) for v in rows]
                                 for u in rows])
    assert gram_det(basis) == gram_det(reduced), "reduction changed the lattice"
    return {"dim": dim, "backend": lll.backend(prefer_fpylll=False),
            "fpylll_available": lll.HAVE_FPYLLL}


@test("polynomials")
def t_polynomials():
    f = poly.pmul(poly.pmul([-5, 1], [7, 1]), [-123456789, 1])
    assert poly.integer_roots(f, bound=10 ** 12) == [-7, 5, 123456789]
    assert sorted(set(poly._bisect_candidates(f, 10 ** 12)) &
                  {-7, 5, 123456789}) == [-7, 5, 123456789], "stdlib root path failed"
    assert poly.poly_gcd(f, poly.pmul([-5, 1], [1, 1])) == [-5, 1]
    assert poly.resultant_bivariate_x({(2, 0): 1, (1, 1): 1, (0, 2): -2},
                                      {(2, 0): 1, (1, 0): -5, (1, 1): -1,
                                       (0, 1): 5}) == []
    return {"checks": 4}


# ------------------------------------------------------------------------ PRNG
@test("lcg-plain")
def t_lcg_plain():
    """The CSCV2026 TYPHON alpha stage shape: prime modulus 2**127-1."""
    r = rng(3)
    m = (1 << 127) - 1
    a, c = r.randrange(2, m), r.randrange(2, m)
    x = r.randrange(2, m)
    outs = []
    for _ in range(6):
        x = (a * x + c) % m
        outs.append(x)
    got = lcg.lcg_recover_params(outs[:5], m)
    assert got["a"] == a and got["c"] == c, "parameters wrong"
    assert got["next"] == outs[5], "prediction wrong"
    return {"modulus": "2**127-1", "outputs_used": 5}


@test("lcg-unknown-modulus")
def t_lcg_unknown():
    r = rng(4)
    m = (1 << 48) - 59
    a, c = r.randrange(2, m), r.randrange(2, m)
    x = r.randrange(2, m)
    outs = []
    for _ in range(8):
        x = (a * x + c) % m
        outs.append(x)
    got = lcg.lcg_recover_modulus(outs)
    assert got.get("modulus") == m and got["a"] == a and got["c"] == c, got
    return {"modulus_bits": m.bit_length()}


@test("lcg-truncated")
def t_lcg_truncated():
    r = rng(5)
    m = (1 << 64) - 59
    a, c = r.randrange(2, m), r.randrange(2, m)
    x = r.randrange(2, m)
    k = 16
    states, highs = [], []
    for _ in range(10):
        x = (a * x + c) % m
        states.append(x)
        highs.append(x >> k)
    got = lcg.truncated_lcg_recover(highs, m, a, c, k, prefer_fpylll=False)
    assert got["states"] == states, got.get("reason")
    return {"dropped_bits": k, "samples": len(highs), "lattice_dim": got["lattice_dim"]}


@test("mt19937")
def t_mt():
    r = rng(6)
    outs = [r.getrandbits(32) for _ in range(624)]
    future = [r.getrandbits(32) for _ in range(5)]
    got = mt19937.predict_next(outs, 5)
    assert got["next"] == future, "prediction diverged"
    return {"words_used": 624}


# ------------------------------------------------------------------------- RSA
@test("hastad")
def t_hastad():
    r = rng(7)
    msg = int.from_bytes(b"CSCV{hastad}", "big")
    pairs = []
    for _ in range(3):
        n = gen_prime(160, r) * gen_prime(160, r)
        pairs.append((n, pow(msg, 3, n)))
    got = rsa.hastad_broadcast(pairs, 3)
    assert got["message"] == msg, got.get("reason")
    bad = rsa.hastad_broadcast(pairs[:2], 3)
    assert bad["message"] is None, "should refuse with fewer than e ciphertexts"
    return {"e": 3, "moduli": 3}


@test("small-e-root")
def t_small_e():
    r = rng(8)
    msg = int.from_bytes(b"short", "big")
    n = gen_prime(256, r) * gen_prime(256, r)
    assert rsa.small_e_root(n, 3, pow(msg, 3, n))["message"] == msg
    return {"e": 3}


@test("common-modulus")
def t_common_modulus():
    r = rng(9)
    n = gen_prime(200, r) * gen_prime(200, r)
    msg = int.from_bytes(b"same message twice", "big")
    got = rsa.common_modulus(n, 3, pow(msg, 3, n), 17, pow(msg, 17, n))
    assert got["message"] == msg, got
    return {"e1": 3, "e2": 17}


@test("wiener")
def t_wiener():
    r = rng(10)
    from math import gcd
    while True:
        p, q = gen_prime(256, r), gen_prime(256, r)
        n = p * q
        phi = (p - 1) * (q - 1)
        d = r.getrandbits(int(0.23 * n.bit_length())) | 1
        if gcd(d, phi) != 1:
            continue
        e = pow(d, -1, phi)
        if e.bit_length() > n.bit_length() - 20:
            break
    got = rsa.wiener(n, e)
    assert got["d"] == d, got
    assert got["p"] * got["q"] == n
    return {"n_bits": n.bit_length(), "d_bits": d.bit_length(),
            "delta": round(d.bit_length() / n.bit_length(), 3)}


@test("boneh-durfee")
def t_bd():
    """Above the Wiener bound is m>=6 territory; the fast case proves the whole
    pipeline (lattice -> resultant -> integer root -> p+q) with try_wiener off."""
    r = rng(11)
    from math import gcd
    n_bits, d_bits, m = 128, 26, 3
    while True:
        p, q = gen_prime(n_bits // 2, r), gen_prime(n_bits // 2, r)
        n = p * q
        if n.bit_length() != n_bits:
            continue
        phi = (p - 1) * (q - 1)
        d = r.getrandbits(d_bits) | 1
        if gcd(d, phi) != 1:
            continue
        e = pow(d, -1, phi)
        if e.bit_length() >= n_bits - 8:
            break
    got = rsa.boneh_durfee(n, e, delta=d_bits / n_bits + 0.02, m=m,
                           try_wiener=False, prefer_fpylll=False)
    assert got.get("p") in (p, q), got.get("reason")
    assert got["d"] == d, "recovered p,q but d mismatched"
    return {"n_bits": n_bits, "d_bits": d_bits, "m": m,
            "delta": round(d_bits / n_bits, 3), "lattice_dim": got["lattice_dim"]}


@test("boneh-durfee-above-wiener", slow=True)
def t_bd_slow():
    r = rng(12)
    from math import gcd
    n_bits, d_bits, m = 128, 34, 7
    while True:
        p, q = gen_prime(n_bits // 2, r), gen_prime(n_bits // 2, r)
        n = p * q
        if n.bit_length() != n_bits:
            continue
        phi = (p - 1) * (q - 1)
        d = r.getrandbits(d_bits) | 1
        if gcd(d, phi) != 1:
            continue
        e = pow(d, -1, phi)
        if e.bit_length() >= n_bits - 8:
            break
    assert rsa.wiener(n, e)["d"] is None, "instance is inside Wiener's reach"
    got = rsa.boneh_durfee(n, e, delta=d_bits / n_bits + 0.02, m=m,
                           try_wiener=False, prefer_fpylll=False)
    assert got.get("p") in (p, q), got.get("reason")
    return {"n_bits": n_bits, "d_bits": d_bits, "m": m,
            "delta": round(d_bits / n_bits, 3)}


@test("coppersmith-high-bits")
def t_coppersmith():
    r = rng(13)
    p_bits, known = 128, 96
    p, q = gen_prime(p_bits, r), gen_prime(p_bits, r)
    n = p * q
    top = p >> (p_bits - known)
    got = rsa.factor_with_known_high_bits(n, top, known, p_bits, m=3, t=3,
                                          prefer_fpylll=False)
    assert got.get("factor") in (p, q), got.get("reason")
    assert got["prefix_matches"], "returned the cofactor without fixing the prefix"
    return {"p_bits": p_bits, "known_bits": known, "unknown_bits": p_bits - known,
            "m": 3, "route": got["route"]}


@test("coppersmith-half", slow=True)
def t_coppersmith_half():
    """Exactly half the bits known -- the CSCV2026 lambda stage shape."""
    r = rng(14)
    p_bits, known = 128, 64
    p, q = gen_prime(p_bits, r), gen_prime(p_bits, r)
    n = p * q
    top = p >> (p_bits - known)
    got = rsa.factor_with_known_high_bits(n, top, known, p_bits, m=12, t=12,
                                          prefer_fpylll=False)
    assert got.get("factor") in (p, q), got.get("reason")
    return {"p_bits": p_bits, "known_bits": known, "m": 12}


@test("pollard-pm1")
def t_pm1():
    r = rng(15)
    smooth = 1
    for q in [q for q in range(2, 300) if nt.is_prime(q)][:12]:
        smooth *= q
    p = smooth * 2 + 1
    while not nt.is_prime(p):
        p += smooth
    n = p * gen_prime(64, r)
    got = rsa.pollard_pm1(n, 400)
    assert got.get("factor") in (p, n // p), got
    return {"n_bits": n.bit_length()}


# ------------------------------------------------------------ discrete log / EC
@test("pohlig-hellman")
def t_ph():
    r = rng(16)
    p = smooth_prime(160, r)
    g = 2
    while pow(g, (p - 1) // 2, p) == 1 and g < 64:
        g += 1
    x = r.randrange(2, p - 1)
    h = pow(g, x, p)
    got = dlog.pohlig_hellman(g, h, p)
    assert got["x"] is not None and pow(g, got["x"], p) == h, got
    report = nt.smoothness(p - 1)
    assert report["pohlig_hellman"] == "cheap", report
    return {"p_bits": p.bit_length(), "largest_prime": got["largest_prime"],
            "order_bits": got["order"].bit_length()}


@test("bsgs")
def t_bsgs():
    p = (1 << 61) - 1
    x = 123456789
    got = dlog.bsgs(37, pow(37, x, p), p, order=1 << 34)
    assert got["x"] == x, got
    return {"p_bits": p.bit_length()}


@test("ecdsa-hnp")
def t_hnp():
    """Short nonces on secp256k1. Few samples keep the pure-Python lattice small;
    the 40-signature / 128-bit-nonce contest shape works too but takes ~39 min
    without fpylll (measured)."""
    r = rng(17)
    params = ec.curve("secp256k1")
    n = params["n"]
    d = r.randrange(1, n)
    pub = ec.pubkey_from_priv(d, params)
    nonce_bits, count = 64, 8
    sigs = []
    for i in range(count):
        k = r.getrandbits(nonce_bits) | 1
        R = ec.ec_mul(k, (params["Gx"], params["Gy"]), params["p"], params["a"])
        rr = R[0] % n
        z = int.from_bytes(hashlib.sha256(b"m%d" % i).digest(), "big") % n
        s = pow(k, -1, n) * (z + d * rr) % n
        sigs.append((rr, s, z))
    got = hnp.ecdsa_recover_biased_nonce(sigs, n, nonce_bits=nonce_bits,
                                         curve_name="secp256k1", pubkey=pub,
                                         prefer_fpylll=False)
    assert got["private_key"] == d, got
    assert got["pubkey_verified"], "recovered without verifying against the pubkey"
    return {"curve": "secp256k1", "signatures": count, "nonce_bits": nonce_bits,
            "lattice_dim": got["lattice_dim"]}


@test("ecdsa-hnp-contest-shape", slow=True)
def t_hnp_slow():
    r = rng(18)
    params = ec.curve("secp256k1")
    n = params["n"]
    d = r.randrange(1, n)
    pub = ec.pubkey_from_priv(d, params)
    sigs = []
    for i in range(40):
        k = r.getrandbits(128)
        R = ec.ec_mul(k, (params["Gx"], params["Gy"]), params["p"], params["a"])
        rr = R[0] % n
        z = int.from_bytes(hashlib.sha256(b"m%d" % i).digest(), "big") % n
        sigs.append((rr, pow(k, -1, n) * (z + d * rr) % n, z))
    got = hnp.ecdsa_recover_biased_nonce(sigs, n, nonce_bits=128,
                                         curve_name="secp256k1", pubkey=pub,
                                         prefer_fpylll=False)
    assert got["private_key"] == d, got
    return {"signatures": 40, "nonce_bits": 128}


@test("ecdsa-nonce-reuse")
def t_reuse():
    r = rng(19)
    params = ec.curve("secp256k1")
    n = params["n"]
    d = r.randrange(1, n)
    k = r.randrange(1, n)
    R = ec.ec_mul(k, (params["Gx"], params["Gy"]), params["p"], params["a"])
    rr = R[0] % n
    z1, z2 = 111111, 222222
    s1 = pow(k, -1, n) * (z1 + d * rr) % n
    s2 = pow(k, -1, n) * (z2 + d * rr) % n
    got = hnp.ecdsa_recover_nonce_reuse((rr, s1, z1), (rr, s2, z2), n)
    assert got["private_key"] == d, got
    return {"curve": "secp256k1"}


# ------------------------------------------------------------------ hash / xor
@test("length-extension")
def t_lenext():
    out = {}
    for algo, hf in (("sha256", hashlib.sha256), ("sha1", hashlib.sha1)):
        secret = b"0123456789abcdef"
        original = b"user=guest&role=user"
        mac = hf(secret + original).hexdigest()
        got = hash_ext.length_extension(algo, mac, len(secret), original,
                                        b"::uid=root::op=exec")
        forged_msg = bytes.fromhex(got["new_message_hex"])
        real = hf(secret + forged_msg).hexdigest()
        assert real == got["forged_digest"], "%s forgery does not verify" % algo
        out[algo] = got["forged_digest"][:16] + "..."
    return out


@test("lfsr")
def t_lfsr():
    """Taps 32,30,26,24 -- the CSCV2026 TYPHON gamma stage register."""
    r = rng(20)
    taps, width = [32, 30, 26, 24], 32
    state = r.getrandbits(width) | 1
    bits = lfsr.lfsr_stream(state, taps, width, 8 * 24)
    got = lfsr.lfsr_reconstruct(bits[:64], taps, width)
    assert got["state"] == state, got.get("reason")
    assert lfsr.lfsr_stream(got["state"], taps, width, len(bits)) == bits
    forward = lfsr.lfsr_predict(bits[:64], taps, width, 128)
    assert forward["next_bits"] == bits[64:64 + 128], "prediction diverged"
    return {"taps": taps, "width": width, "bits_used": 64}


@test("berlekamp-massey")
def t_bm():
    r = rng(21)
    taps, width = [32, 30, 26, 24], 32
    state = r.getrandbits(width) | 1
    bits = lfsr.lfsr_stream(state, taps, width, 4 * width + 32)
    got = lfsr.berlekamp_massey(bits)
    rec = lfsr.lfsr_reconstruct(bits[:2 * got["width"]], got["taps"], got["width"])
    assert rec["state"] is not None, rec.get("reason")
    replay = lfsr.lfsr_stream(rec["state"], got["taps"], got["width"], len(bits))
    assert replay == bits, "recovered register does not reproduce the keystream"
    return {"linear_complexity": got["width"], "taps_found": got["taps"]}


@test("xor-crib-drag")
def t_xor():
    r = rng(22)
    ks = bytes(r.getrandbits(8) for _ in range(40))
    a = xor.xor_bytes(ks, b"flag{keystream_was_reused_here_ok}      "[:40])
    b = xor.xor_bytes(ks, b"Content-Type: text/html; charset=utf-8  "[:40])
    got = xor.crib_drag(a, b, "Content-Type")
    assert any(h["offset"] == 0 and h["other_plaintext"].startswith("flag{")
               for h in got["hits"]), got["hits"][:3]
    assert xor.single_byte_xor(bytes(c ^ 0x5A for c in
                                    b"the quick brown fox"))["candidates"][0]["key"] == 0x5A
    return {"hits": len(got["hits"])}


@test("identify-shapes")
def t_identify_shapes():
    """The CLI triage detectors: they fire on the shape, and stay quiet otherwise.

    Positive fixture: a real LCG stream beside its modulus, a real secp256k1
    public point beside a signature list, and three nonce/ct/tag hex triples.
    Negative fixture: the same building blocks arranged so none of the three
    shapes is present -- a 512-bit (n, c) pair, a non-LCG run of same-width
    integers, and a two-field iv/data blob.
    """
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import crypto_attack as ca                             # the CLI, not the package

    r = rng(31)
    m = (1 << 127) - 1
    a, c = r.randrange(2, m), r.randrange(2, m)
    x = r.randrange(2, m)
    outs = []
    for _ in range(5):
        x = (a * x + c) % m
        outs.append(x)
    C = ec.CURVES["secp256k1"]
    d = r.randrange(1, C["n"])
    Q = ec.ec_mul(d, (C["Gx"], C["Gy"]), C["p"], C["a"])
    sigs = []
    for i in range(4):
        k = r.randrange(1, C["n"])
        R = ec.ec_mul(k, (C["Gx"], C["Gy"]), C["p"], C["a"])
        z = int.from_bytes(hashlib.sha256(b"m%d" % i).digest(), "big") % C["n"]
        rr = R[0] % C["n"]
        sigs.append({"r": rr, "s": nt.inverse(k, C["n"]) * (z + d * rr) % C["n"],
                     "z": z})

    def hx(n):
        return bytes(r.getrandbits(8) for _ in range(n)).hex()

    positive = {
        "stage1": {"mod": m, "stream": outs},
        "point": {"px": Q[0], "py": Q[1]},
        "log": sigs,
        "s1": {"iv": hx(12), "body": hx(64), "mac": hx(16)},
        "s2": {"iv": hx(12), "body": hx(96), "mac": hx(16)},
        "s3": {"iv": hx(12), "body": hx(48), "mac": hx(16)},
    }
    negative = {
        "vault": {"n": r.getrandbits(512), "c": r.getrandbits(512)},
        "tickets": [r.getrandbits(64) for _ in range(10)],
        "blob": {"iv": hx(16), "data": hx(64)},
    }

    def fired(doc):
        ints, hexes, hex_text, int_lists, objects = ca._walk_structure(doc)
        return {
            "lcg": ca._detect_lcg(ints, int_lists, objects)[0],
            "ecdsa": ca._detect_ecdsa(ints, int_lists, objects)[0],
            "aead": ca._detect_aead(hex_text, objects)[0],
        }

    pos = fired(positive)
    assert any("LCG-shaped at /stage1/stream" in o for o in pos["lcg"]), pos["lcg"]
    assert any("satisfy the secp256k1 curve equation" in o
               for o in pos["ecdsa"]), pos["ecdsa"]
    assert any("signature-shaped list at /log: 4 tuples" in o
               for o in pos["ecdsa"]), pos["ecdsa"]
    assert any("3 sibling AEAD-shaped blobs" in o and "16-byte tag" in o
               for o in pos["aead"]), pos["aead"]
    neg = fired(negative)
    assert neg == {"lcg": [], "ecdsa": [], "aead": []}, neg
    return {"positive_observations": sum(len(v) for v in pos.values()),
            "negative_observations": sum(len(v) for v in neg.values())}


# --------------------------------------------------------------------- runner
# ------------------------------------------------------------------ real data
@test("real_typhon")
def t_real_typhon():
    """Stages alpha..zeta of the REAL CSCV2026 TYPHON handout, through Set A only.

    This is the test that matters: a self-test built from its own synthetic
    instances proves the code is self-consistent, not that it solves a contest
    handout. Every stage key here is checked by an AES-GCM tag, so a wrong
    recovery cannot pass -- decrypt_and_verify raises instead.

    Skips, never fails, when the handout or pycryptodome is absent, so this file
    still runs on a bare Python as its docstring promises.
    """
    if not os.path.exists(TYPHON):
        raise Skip("handout not on this machine: %s" % TYPHON)
    try:
        from Crypto.Cipher import AES
        from Crypto.Util.number import long_to_bytes as L2B, bytes_to_long as B2L
    except ImportError:
        raise Skip("pycryptodome not installed")

    with open(TYPHON, encoding="utf-8") as fh:
        d = json.load(fh)

    def dec(key, blob):
        return AES.new(key, AES.MODE_GCM, nonce=bytes.fromhex(blob["N"])).decrypt_and_verify(
            bytes.fromhex(blob["C"]), bytes.fromhex(blob["T"]))

    # alpha: truncated LCG mod 2**127-1 -> the next output keys the alpha blob
    al = d["\u03b1"]
    got = lcg.lcg_recover_params(al["out"], al["M"])
    assert got.get("next") is not None, got
    plain = dec(hashlib.sha256(L2B(got["next"], 16)).digest()[:16], al["\u03a6"])

    # beta: Hastad broadcast, e=3 over three moduli
    vals = [B2L(plain[i:i + 16]) for i in range(0, 96, 16)]
    had = rsa.hastad_broadcast(list(zip(vals[:3], vals[3:])), e=3)
    assert had.get("message") is not None, had
    s1 = L2B(had["message"], 15)

    # gamma: Wiener -- NOTE Set A takes (n, e), the reverse of the usual (e, n)
    gd = json.loads(dec(hashlib.sha256(s1).digest()[:16], d["\u03b3"]["\u03a6"]))
    wn = rsa.wiener(gd["nw"], gd["ew"])
    assert wn.get("d") is not None, wn
    gk = L2B(pow(gd["wc"], wn["d"], gd["nw"]), 16)
    p2 = AES.new(gk, AES.MODE_GCM, nonce=bytes.fromhex(gd["gn"])).decrypt_and_verify(
        bytes.fromhex(gd["c2"]), bytes.fromhex(gd["t2"]))

    # delta: 32-bit LFSR, taps 32/30/26/24, cross-checked by Berlekamp-Massey
    bits = lfsr.lfsr_bytes_to_bits(p2[:8])
    rec = lfsr.lfsr_predict(bits, [32, 30, 26, 24], 32, 128)
    assert rec.get("state") is not None, rec
    bm = lfsr.berlekamp_massey(bits)
    assert lfsr.taps_for_width(bm["recurrence_taps"], 32) == [24, 26, 30, 32], bm
    kl = lfsr.lfsr_bits_to_bytes(rec["next_bits"])

    # epsilon: Pohlig-Hellman, p-1 smooth with largest prime 193
    pd = json.loads(dec(kl, d["\u03b4"]["\u03a6"]))
    ph = dlog.pohlig_hellman(pd["ph_g"], pd["ph_h"], pd["ph_p"])
    assert ph.get("x") is not None and ph.get("largest_prime") == 193, ph

    # zeta: SHA-256 length extension -> the forged digest keys the eta stage
    zd = json.loads(dec(hashlib.sha256(L2B(ph["x"], 16)).digest()[:16], d["\u03b6"]["\u03a6"]))
    le = hash_ext.length_extension("sha256", zd["sha_mac"], zd["secret_len"],
                                   bytes.fromhex(zd["sha_msg"]), b"::uid=root::op=exec")
    ks = bytes.fromhex(le["forged_digest"])[:16]
    eta = dec(hashlib.sha256(ks).digest()[:16], d["\u03b7"]["\u03a6"])
    assert eta.startswith(b"TYPHON C2 SESSION LOG"), eta[:40]

    return {"stages": "alpha..zeta",
            "wiener_d_bits": wn["d"].bit_length(),
            "lfsr_state": hex(rec["state"]),
            "ph_largest_prime": ph["largest_prime"],
            "confirmed_by": "one AES-GCM tag per stage"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--slow", action="store_true", help="include the large lattice cases")
    ap.add_argument("--only", help="comma-separated test names")
    ap.add_argument("--json", action="store_true", help="compact JSON output")
    args = ap.parse_args()

    wanted = set(args.only.split(",")) if args.only else None
    results, failures = [], 0
    started = time.time()
    for name, fn, slow in TESTS:
        if wanted and name not in wanted:
            continue
        if slow and not args.slow and not wanted:
            results.append({"test": name, "status": "skipped",
                            "detail": "slow; run with --slow"})
            continue
        t0 = time.time()
        try:
            detail = fn() or {}
            status = "pass"
        except Skip as exc:                            # absent artifact, not a failure
            results.append({"test": name, "status": "skipped",
                            "detail": {"reason": str(exc)}})
            if not args.json:
                print("%-28s %-7s %6.2fs  %s" % (name, "skipped", 0.0,
                                                 json.dumps({"reason": str(exc)})), flush=True)
            continue
        except AssertionError as exc:
            status, detail, failures = "FAIL", {"assertion": str(exc)}, failures + 1
        except Exception as exc:                       # noqa: BLE001
            status = "ERROR"
            detail = {"exception": "%s: %s" % (type(exc).__name__, exc)}
            failures += 1
        results.append({"test": name, "status": status,
                        "seconds": round(time.time() - t0, 2), "detail": detail})
        if not args.json:
            print("%-28s %-7s %6.2fs  %s" % (name, status, results[-1].get("seconds", 0),
                                             json.dumps(detail, default=str)), flush=True)

    summary = {
        "mode": "crypto-selftest",
        "seed": SEED,
        "lll_backend": lll.backend(),
        "optional_libs": {"fpylll": lll.HAVE_FPYLLL, "mpmath": poly.HAVE_MPMATH},
        "total": len([r for r in results if r["status"] != "skipped"]),
        "passed": len([r for r in results if r["status"] == "pass"]),
        "failed": failures,
        "skipped": len([r for r in results if r["status"] == "skipped"]),
        "seconds": round(time.time() - started, 2),
        "results": results,
    }
    if args.json:
        print(json.dumps(summary, default=str))
    else:
        print(json.dumps({k: v for k, v in summary.items() if k != "results"},
                         indent=2, default=str))
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
