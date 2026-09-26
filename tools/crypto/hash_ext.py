"""Merkle-Damgard length extension for SHA-1 and SHA-256.

Both compression functions are reimplemented here with a settable IV, which is
the whole point: a digest of secret||message IS the chaining state, so you can
keep hashing from it without knowing the secret.
"""
import struct

__all__ = ["md_padding", "sha1_from_state", "sha256_from_state",
           "length_extension", "ALGORITHMS"]

ALGORITHMS = ("sha1", "sha256")

_K256 = [
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1,
    0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
    0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786,
    0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147,
    0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
    0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b,
    0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a,
    0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
    0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
]
_MASK = 0xFFFFFFFF


def _rotr(x, n):
    return ((x >> n) | (x << (32 - n))) & _MASK


def _rotl(x, n):
    return ((x << n) | (x >> (32 - n))) & _MASK


def md_padding(message_len, big_endian=True):
    """The Merkle-Damgard padding a message of this length would receive."""
    pad = b"\x80" + b"\x00" * ((55 - message_len) % 64)
    bits = message_len * 8
    return pad + (struct.pack(">Q", bits) if big_endian else struct.pack("<Q", bits))


def _sha256_block(state, block):
    w = list(struct.unpack(">16I", block))
    for i in range(16, 64):
        s0 = _rotr(w[i - 15], 7) ^ _rotr(w[i - 15], 18) ^ (w[i - 15] >> 3)
        s1 = _rotr(w[i - 2], 17) ^ _rotr(w[i - 2], 19) ^ (w[i - 2] >> 10)
        w.append((w[i - 16] + s0 + w[i - 7] + s1) & _MASK)
    a, b, c, d, e, f, g, h = state
    for i in range(64):
        t1 = (h + (_rotr(e, 6) ^ _rotr(e, 11) ^ _rotr(e, 25))
              + ((e & f) ^ (~e & g)) + _K256[i] + w[i]) & _MASK
        t2 = ((_rotr(a, 2) ^ _rotr(a, 13) ^ _rotr(a, 22))
              + ((a & b) ^ (a & c) ^ (b & c))) & _MASK
        h, g, f, e, d, c, b, a = g, f, e, (d + t1) & _MASK, c, b, a, (t1 + t2) & _MASK
    return [(x + y) & _MASK for x, y in zip(state, [a, b, c, d, e, f, g, h])]


def _sha1_block(state, block):
    w = list(struct.unpack(">16I", block))
    for i in range(16, 80):
        w.append(_rotl(w[i - 3] ^ w[i - 8] ^ w[i - 14] ^ w[i - 16], 1))
    a, b, c, d, e = state
    for i in range(80):
        if i < 20:
            f, k = (b & c) | (~b & d), 0x5A827999
        elif i < 40:
            f, k = b ^ c ^ d, 0x6ED9EBA1
        elif i < 60:
            f, k = (b & c) | (b & d) | (c & d), 0x8F1BBCDC
        else:
            f, k = b ^ c ^ d, 0xCA62C1D6
        a, b, c, d, e = ((_rotl(a, 5) + (f & _MASK) + e + k + w[i]) & _MASK,
                         a, _rotl(b, 30), c, d)
    return [(x + y) & _MASK for x, y in zip(state, [a, b, c, d, e])]


def _state_from_digest(digest, words):
    if len(digest) != words * 4:
        raise ValueError("digest must be %d bytes for this algorithm" % (words * 4))
    return [int.from_bytes(digest[i * 4:i * 4 + 4], "big") for i in range(words)]


def sha256_from_state(digest, data, total_prefix_len):
    """Continue SHA-256 from a known digest. total_prefix_len = bytes already
    hashed INCLUDING their padding."""
    state = _state_from_digest(digest, 8)
    block = data + md_padding(total_prefix_len + len(data))
    for i in range(0, len(block), 64):
        state = _sha256_block(state, block[i:i + 64])
    return b"".join(struct.pack(">I", s) for s in state)


def sha1_from_state(digest, data, total_prefix_len):
    state = _state_from_digest(digest, 5)
    block = data + md_padding(total_prefix_len + len(data))
    for i in range(0, len(block), 64):
        state = _sha1_block(state, block[i:i + 64])
    return b"".join(struct.pack(">I", s) for s in state)


def length_extension(algorithm, mac_hex, secret_len, original, append):
    """Forge MAC(secret || original || glue || append) from MAC(secret || original).

    APPLICABILITY: the MAC is a raw Merkle-Damgard hash of secret||message
    (sha1/sha256), you know the message and the LENGTH of the secret, and the
    server appends nothing after your data. Falsifier: the MAC is HMAC, or a
    sponge (SHA-3/Keccak/BLAKE2) -- neither extends.

    Returns the forged digest and the exact bytes to submit as the new message:
    original || glue_padding || append.
    """
    algorithm = algorithm.lower().replace("-", "")
    if algorithm not in ALGORITHMS:
        raise ValueError("algorithm must be one of %s" % (ALGORITHMS,))
    original = _as_bytes(original)
    append = _as_bytes(append)
    digest = bytes.fromhex(mac_hex.strip())
    secret_len = int(secret_len)
    known_len = secret_len + len(original)
    glue = md_padding(known_len)
    total_prefix = known_len + len(glue)
    fn = sha256_from_state if algorithm == "sha256" else sha1_from_state
    forged = fn(digest, append, total_prefix)
    new_message = original + glue + append
    return {
        "algorithm": algorithm,
        "forged_digest": forged.hex(),
        "new_message_hex": new_message.hex(),
        "new_message_repr": repr(new_message),
        "glue_padding_hex": glue.hex(),
        "secret_len_assumed": secret_len,
        "total_hashed_len": total_prefix + len(append),
    }


def _as_bytes(value):
    if isinstance(value, bytes):
        return value
    if isinstance(value, str):
        if value.startswith("hex:"):
            return bytes.fromhex(value[4:])
        return value.encode()
    raise TypeError("expected bytes or str, got %r" % type(value))
