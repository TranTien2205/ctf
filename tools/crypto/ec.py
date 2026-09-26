"""Minimal short-Weierstrass elliptic curve arithmetic over a prime field.

Only what an ECDSA recovery needs: add, scalar multiply, and a check that a
recovered private key really produces the published public point.
"""
from .numtheory import inverse

__all__ = ["CURVES", "curve", "ec_add", "ec_mul", "on_curve", "pubkey_from_priv"]

CURVES = {
    "secp256k1": {
        "p": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F,
        "a": 0,
        "b": 7,
        "n": 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141,
        "Gx": 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
        "Gy": 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
    },
    "secp256r1": {
        "p": 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF,
        "a": 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFC,
        "b": 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B,
        "n": 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551,
        "Gx": 0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
        "Gy": 0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5,
    },
}


def curve(name_or_params):
    if isinstance(name_or_params, dict):
        return dict(name_or_params)
    if name_or_params not in CURVES:
        raise ValueError("unknown curve %r; known: %s"
                         % (name_or_params, ", ".join(sorted(CURVES))))
    return dict(CURVES[name_or_params])


def ec_add(P, Q, p, a=0):
    """Add two affine points; None is the point at infinity."""
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if x1 == x2 and y1 == y2:
        inv = inverse(2 * y1 % p, p)
        if inv is None:
            return None
        lam = (3 * x1 * x1 + a) * inv % p
    else:
        inv = inverse((x2 - x1) % p, p)
        if inv is None:
            return None
        lam = (y2 - y1) * inv % p
    x3 = (lam * lam - x1 - x2) % p
    return x3, (lam * (x1 - x3) - y1) % p


def ec_mul(k, P, p, a=0):
    R, Q = None, P
    k = int(k)
    if k < 0:
        k, Q = -k, (P[0], (-P[1]) % p)
    while k:
        if k & 1:
            R = ec_add(R, Q, p, a)
        Q = ec_add(Q, Q, p, a)
        k >>= 1
    return R


def on_curve(P, p, a, b):
    if P is None:
        return True
    x, y = P
    return (y * y - x * x * x - a * x - b) % p == 0


def pubkey_from_priv(d, params):
    return ec_mul(d, (params["Gx"], params["Gy"]), params["p"], params.get("a", 0))
