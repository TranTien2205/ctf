#!/usr/bin/env python3
"""De Bruijn cyclic pattern — the pwntools cyclic()/cyclic_find() absent here.

pwn_triage tells the agent to find the saved-return offset by feeding a
cyclic pattern and reading the faulting address; nothing in this tree makes
one. Same construction as pwntools: alphabet b'abcdefghijklmnopqrstuvwxyz',
subsequence length 4 — so a crash register read gives a unique offset and
offsets found with pwntools documentation still line up.
"""
from __future__ import annotations

ALPHABET = b"abcdefghijklmnopqrstuvwxyz"
N = 4


def de_bruijn(alphabet: bytes = ALPHABET, n: int = N) -> bytes:
    """FKM prefer-smallest de Bruijn sequence B(k, n), linearized."""
    k = len(alphabet)
    a = [0] * (k * n)
    out = bytearray()

    def db(t: int, p: int) -> None:
        if t > n:
            if n % p == 0:
                out.extend(alphabet[a[j]] for j in range(1, p + 1))
        else:
            a[t] = a[t - p]
            db(t + 1, p)
            for j in range(a[t - p] + 1, k):
                a[t] = j
                db(t + 1, t)

    db(1, 1)
    return bytes(out)


_SEQ = de_bruijn()


def cyclic(length: int) -> bytes:
    if length < 0:
        raise ValueError("length must be >= 0")
    if length > len(_SEQ):
        raise ValueError(f"length beyond unique region ({len(_SEQ)}) — offsets stop being unique")
    return _SEQ[:length]


def cyclic_find(needle) -> int:
    """Offset of a 4-byte value (bytes, int, '0x…', 'aaaa', or little-endian int)."""
    if isinstance(needle, int):
        needle = needle.to_bytes(4, "little")
    elif isinstance(needle, str):
        s = needle.strip()
        if s.startswith("0x"):
            needle = int(s, 16).to_bytes(4, "little")
        else:
            needle = s.encode()[:4]
    if len(needle) != 4:
        raise ValueError("needle must resolve to exactly 4 bytes")
    pos = _SEQ.find(needle)
    if pos == -1:  # maybe it arrived big-endian from a register dump
        rev = needle[::-1]
        pos = _SEQ.find(rev)
        if pos != -1:
            return pos
    return pos
