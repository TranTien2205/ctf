"""XOR keystream reuse: crib dragging and single-byte XOR."""
__all__ = ["xor_bytes", "crib_drag", "single_byte_xor", "recover_keystream"]

_PRINTABLE = set(range(32, 127)) | {9, 10, 13}


def xor_bytes(a, b):
    return bytes(x ^ y for x, y in zip(a, b))


def crib_drag(ct_a, ct_b, crib):
    """Drag a known plaintext fragment across two ciphertexts sharing a keystream.

    APPLICABILITY: two ciphertexts under the SAME keystream (a reused CTR/OFB
    nonce, a one-time pad used twice, a stream cipher with a fixed key) and a
    guessable fragment such as "flag{" or "Content-Type". Falsifier: the XOR of
    the two ciphertexts yields nothing printable at any offset under any crib --
    then the keystreams differ.

    Returns the offsets where the crib produces printable text in the other
    message, each with what the other plaintext would then read.
    """
    if isinstance(crib, str):
        crib = crib.encode()
    delta = xor_bytes(ct_a, ct_b)
    hits = []
    for off in range(0, max(1, len(delta) - len(crib) + 1)):
        window = delta[off:off + len(crib)]
        if len(window) < len(crib):
            break
        guess = xor_bytes(window, crib)
        if all(b in _PRINTABLE for b in guess):
            hits.append({"offset": off, "other_plaintext": guess.decode("latin1"),
                         "keystream_hex": xor_bytes(ct_a[off:off + len(crib)], crib).hex()})
    return {"xor_of_ciphertexts_hex": delta.hex(), "crib": crib.decode("latin1"),
            "hits": hits}


def recover_keystream(ciphertext, known_plaintext, offset=0):
    """Keystream bytes implied by a known plaintext fragment at a known offset."""
    if isinstance(known_plaintext, str):
        known_plaintext = known_plaintext.encode()
    seg = ciphertext[offset:offset + len(known_plaintext)]
    return {"offset": offset, "keystream_hex": xor_bytes(seg, known_plaintext).hex()}


def single_byte_xor(ciphertext, top=3):
    """Break single-byte XOR by printable-character score.

    APPLICABILITY: the ciphertext is short and the key is one byte. Falsifier: no
    key produces mostly printable output -- the key is longer than one byte.
    """
    scored = []
    for k in range(256):
        pt = bytes(b ^ k for b in ciphertext)
        score = sum(1 for b in pt if b in _PRINTABLE) + 2 * pt.count(b" ")
        scored.append((score, k, pt))
    scored.sort(key=lambda item: -item[0])
    return {"candidates": [{"key": k, "score": s, "plaintext": pt.decode("latin1")}
                           for s, k, pt in scored[:top]]}
