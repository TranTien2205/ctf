"""Mersenne Twister state recovery (MT19937), the default PRNG behind
random.getrandbits in Python, mt_rand in PHP and Random in Ruby.
"""
__all__ = ["untemper", "temper", "clone_state", "predict_next"]

_W = 0xFFFFFFFF


def _unshift_right(x, shift):
    res = x
    for _ in range(32 // shift + 1):
        res = x ^ (res >> shift)
    return res & _W


def _unshift_left(x, shift, mask):
    res = x
    for _ in range(32 // shift + 1):
        res = x ^ ((res << shift) & mask)
    return res & _W


def temper(y):
    y ^= y >> 11
    y ^= (y << 7) & 0x9D2C5680
    y ^= (y << 15) & 0xEFC60000
    y ^= y >> 18
    return y & _W


def untemper(y):
    """Invert MT19937's output tempering: one output word -> one state word."""
    y &= _W
    y = _unshift_right(y, 18)
    y = _unshift_left(y, 15, 0xEFC60000)
    y = _unshift_left(y, 7, 0x9D2C5680)
    return _unshift_right(y, 11)


def clone_state(outputs):
    """Recover the internal state from 624 consecutive 32-bit outputs.

    APPLICABILITY: the target leaks whole 32-bit words from an untruncated
    MT19937 -- random.getrandbits(32), or two 16-bit halves you can rejoin.
    Falsifier: fewer than 624 consecutive words, or the outputs are truncated or
    reduced modulo something, in which case this exact method cannot work (a
    GF(2) solve over the bits can, which is a different tool).
    """
    outs = [int(v) & _W for v in outputs]
    if len(outs) < 624:
        return {"state": None, "reason": "need 624 consecutive 32-bit outputs, got %d"
                                         % len(outs)}
    return {"state": [untemper(v) for v in outs[-624:]], "words_used": 624}


def predict_next(outputs, count=1):
    """Predict the next outputs of a Python random.Random from 624 words."""
    import random
    got = clone_state(outputs)
    if got["state"] is None:
        return got
    rng = random.Random()
    rng.setstate((3, tuple(got["state"]) + (624,), None))
    got["next"] = [rng.getrandbits(32) for _ in range(int(count))]
    return got
