"""LFSR keystream attacks: reconstruct the register, or find the taps first.

Convention (matches the usual CTF Fibonacci LFSR, and the CSCV2026 TYPHON one):
the register is `width` bits, the output bit is the LSB, the feedback is the XOR
of the bits at the 1-indexed `taps` positions counted from the LSB, and the
feedback bit is shifted into the MSB.
"""
__all__ = ["lfsr_stream", "lfsr_bits_to_bytes", "lfsr_bytes_to_bits",
           "lfsr_reconstruct", "berlekamp_massey", "taps_for_width",
           "lfsr_predict"]


def lfsr_stream(state, taps, width, nbits):
    """Clock the register and return `nbits` output bits as a list of 0/1."""
    st, out = int(state), []
    mask = (1 << width) - 1
    tapmask = 0
    for t in taps:
        tapmask |= 1 << (int(t) - 1)
    for _ in range(nbits):
        out.append(st & 1)
        fb = bin(st & tapmask).count("1") & 1
        st = ((st >> 1) | (fb << (width - 1))) & mask
    return out


def lfsr_bits_to_bytes(bits):
    """Pack output bits MSB-first into bytes, the usual keystream convention."""
    if len(bits) % 8:
        raise ValueError("bit count must be a multiple of 8")
    v = 0
    for b in bits:
        v = (v << 1) | (b & 1)
    return v.to_bytes(len(bits) // 8, "big")


def lfsr_bytes_to_bits(data):
    """Unpack bytes into 0/1 bits MSB-first: the inverse of lfsr_bits_to_bytes.

    APPLICABILITY: a keystream arrived as bytes -- a decrypted blob, a file, a
    hex field -- and lfsr_reconstruct or berlekamp_massey needs it as bits.
    """
    return [(b >> i) & 1 for b in data for i in range(7, -1, -1)]


def taps_for_width(recurrence_taps, width):
    """Renumber Berlekamp-Massey recurrence indices as taps for a register of
    the given width.

    APPLICABILITY: berlekamp_massey found the MINIMAL register (linear
    complexity L), but the real register is known from source to be wider. A
    width-W register and the minimal width-L one emit the same sequence; only
    the tap numbering differs, so the taps this module wants are
    width + 1 - index.

    Falsifier: the returned set does not match the tap set the source states --
    then the sequence is not a plain LFSR of that width.
    """
    return sorted(int(width) + 1 - int(i) for i in recurrence_taps)


def lfsr_reconstruct(bits, taps, width):
    """Recover the initial register state from a known keystream run.

    APPLICABILITY: the tap positions and register width are known (from source,
    a datasheet or Berlekamp-Massey) and you hold at least `width` consecutive
    output bits. Falsifier: replaying the recovered state does not reproduce the
    keystream you were given.

    Solves the GF(2) linear system output = M * initial_state, so it works for
    any tap set and any output position, not only the case where the first
    `width` output bits are the state.
    """
    bits = [int(b) & 1 for b in bits]
    if len(bits) < width:
        return {"state": None, "reason": "need at least %d output bits" % width}
    cols = [lfsr_stream(1 << j, taps, width, len(bits)) for j in range(width)]
    rows = []
    for i, target in enumerate(bits):
        r = 0
        for j in range(width):
            if cols[j][i]:
                r |= 1 << j
        rows.append((r, target))
    # Gaussian elimination over GF(2)
    piv = {}
    for r, t in rows:
        while r:
            b = r.bit_length() - 1
            if b not in piv:
                piv[b] = (r, t)
                break
            pr, pt = piv[b]
            r ^= pr
            t ^= pt
        else:
            if t:
                return {"state": None, "reason": "inconsistent system: taps or width wrong"}
    if len(piv) < width:
        return {"state": None, "reason": "underdetermined: %d of %d bits pinned; "
                                         "supply more keystream" % (len(piv), width)}
    state = 0
    for b in sorted(piv, reverse=True):
        r, t = piv[b]
        val = t
        rr = r & ~(1 << b)
        while rr:
            j = rr.bit_length() - 1
            val ^= (state >> j) & 1
            rr &= ~(1 << j)
        if val:
            state |= 1 << b
    if lfsr_stream(state, taps, width, len(bits)) != bits:
        return {"state": None, "reason": "solution does not replay the keystream"}
    return {"state": state, "state_hex": hex(state), "width": width,
            "taps": list(taps), "bits_used": len(bits)}


def berlekamp_massey(bits):
    """Minimal LFSR that generates this bit sequence: find the taps.

    APPLICABILITY: you hold a keystream but NOT the tap positions. Feed at least
    2*width bits. Returns the linear complexity (register width) and the tap
    positions in this module's 1-indexed-from-LSB convention, ready to hand to
    lfsr_reconstruct.
    """
    s = [int(b) & 1 for b in bits]
    n = len(s)
    C, B = [1] + [0] * n, [1] + [0] * n
    L, mlen, b = 0, -1, 1
    for N in range(n):
        d = s[N]
        for i in range(1, L + 1):
            d ^= C[i] & s[N - i]
        if d:
            T = C[:]
            shift = N - mlen
            for i in range(0, n + 1 - shift):
                C[i + shift] ^= B[i]
            if 2 * L <= N:
                L, mlen, B = N + 1 - L, N, T
    poly = C[:L + 1]
    # C(x) = 1 + c1 x + ... + cL x^L gives the RECURRENCE over the output bits:
    # s[N] = XOR of s[N-i] for every i with c_i = 1. In the shift-right register
    # used here, recurrence index i is the register position (L + 1 - i) counted
    # from the LSB, so the two tap lists are reciprocal. "taps" below is already
    # in this module's convention and can be passed straight to lfsr_reconstruct.
    recurrence = [i for i in range(1, L + 1) if poly[i]]
    taps = sorted(L + 1 - i for i in recurrence)
    return {"width": L, "taps": taps, "recurrence_taps": recurrence,
            "feedback_poly": poly, "bits_used": n, "sufficient": n >= 2 * L}


def lfsr_predict(bits, taps, width, nbits):
    """Extend a keystream forward after reconstructing the state."""
    got = lfsr_reconstruct(bits, taps, width)
    if got["state"] is None:
        return got
    full = lfsr_stream(got["state"], taps, width, len(bits) + nbits)
    got["next_bits"] = full[len(bits):]
    return got
