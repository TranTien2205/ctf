"""Standard-attack library for CTF cryptography.

One tested function per textbook attack, each keyed to the observable that says
"use me". Nothing here is mandatory-dependency: fpylll, sympy, mpmath and
pycryptodome are all optional, and every lattice attack falls back to the
pure-Python LLL in `crypto.lll`.

    import sys; sys.path.insert(0, "/home/kali/ctf-v2/tools")
    from crypto import rsa_attacks
    rsa_attacks.wiener(n, e)

The command line wrapper is ../crypto_attack.py; the self-test is
crypto/selftest.py.
"""
from . import (numtheory, polynomials, lll, ec, hnp, lcg, lfsr, dlog, hash_ext,
               rsa_attacks, mt19937, xor)

__all__ = ["numtheory", "polynomials", "lll", "ec", "hnp", "lcg", "lfsr", "dlog",
           "hash_ext", "rsa_attacks", "mt19937", "xor", "ATTACKS", "applicability",
           "describe_all"]

# name -> (callable, primary result key, family). The primary key is the field a
# caller should test: when it is None the attack did not apply and the dict
# carries a "reason".
ATTACKS = {
    "hastad":                (rsa_attacks.hastad_broadcast, "message", "rsa"),
    "small-e-root":          (rsa_attacks.small_e_root, "message", "rsa"),
    "common-modulus":        (rsa_attacks.common_modulus, "message", "rsa"),
    "wiener":                (rsa_attacks.wiener, "d", "rsa"),
    "boneh-durfee":          (rsa_attacks.boneh_durfee, "p", "rsa-lattice"),
    "boneh-durfee-escalate": (rsa_attacks.boneh_durfee_escalate, "p", "rsa-lattice"),
    "coppersmith-high-bits": (rsa_attacks.factor_with_known_high_bits, "factor",
                              "rsa-lattice"),
    "coppersmith-core":      (rsa_attacks.coppersmith_high_bits, "factor",
                              "rsa-lattice"),
    "fermat":                (rsa_attacks.fermat_factor, None, "rsa"),
    "batch-gcd":             (rsa_attacks.batch_gcd_shared_prime, None, "rsa"),
    "pollard-pm1":           (rsa_attacks.pollard_pm1, "factor", "rsa"),
    "rsa-decrypt":           (rsa_attacks.rsa_decrypt_with_factors, "message", "rsa"),
    "eth-root":              (numtheory.eth_root_mod_composite, None, "rsa"),
    "factor-from-d":         (numtheory.factor_from_d_or_phi, None, "rsa"),
    "pohlig-hellman":        (dlog.pohlig_hellman, "x", "dlog"),
    "bsgs":                  (dlog.bsgs, "x", "dlog"),
    "smoothness":            (numtheory.smoothness, None, "dlog"),
    "lcg-recover":           (lcg.lcg_recover_params, "a", "prng"),
    "lcg-unknown-modulus":   (lcg.lcg_recover_modulus, "a", "prng"),
    "lcg-truncated":         (lcg.truncated_lcg_recover, "states", "prng-lattice"),
    "mt19937-clone":         (mt19937.predict_next, "state", "prng"),
    "lfsr-recover":          (lfsr.lfsr_reconstruct, "state", "prng"),
    "lfsr-predict":          (lfsr.lfsr_predict, "state", "prng"),
    "berlekamp-massey":      (lfsr.berlekamp_massey, None, "prng"),
    "length-extension":      (hash_ext.length_extension, "forged_digest", "hash"),
    "hnp-ecdsa":             (hnp.ecdsa_recover_biased_nonce, "private_key",
                              "ecdsa-lattice"),
    "ecdsa-nonce-reuse":     (hnp.ecdsa_recover_nonce_reuse, "private_key", "ecdsa"),
    "hnp":                   (hnp.hnp_solve, "alpha", "lattice"),
    "crib-drag":             (xor.crib_drag, None, "xor"),
    "single-byte-xor":       (xor.single_byte_xor, None, "xor"),
    "nth-root":              (numtheory.integer_nth_root, None, "helper"),
    "crt":                   (numtheory.crt, None, "helper"),
}


def applicability(name):
    """The APPLICABILITY paragraph from the attack's own docstring."""
    fn = ATTACKS[name][0]
    doc = (fn.__doc__ or "").split("APPLICABILITY:")
    if len(doc) < 2:
        return (fn.__doc__ or "").strip().splitlines()[0] if fn.__doc__ else ""
    text = doc[1].split("\n\n")[0]
    return " ".join(text.split())


def describe_all():
    return [{"attack": name, "family": meta[2], "function":
             meta[0].__module__.split(".")[-1] + "." + meta[0].__name__,
             "primary_key": meta[1], "applicability": applicability(name)}
            for name, meta in sorted(ATTACKS.items())]
