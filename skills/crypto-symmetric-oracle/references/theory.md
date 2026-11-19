# Theory — why each attack works, one paragraph each

## ECB leaks structure

Each plaintext block encrypts independently under the same key: E(p_i) is a
pure function of p_i. Identical p_i → identical c_i, and any spliced block
decrypts as its own plaintext. Determinism + independence is the whole flaw.

## CBC padding oracle (Vaudenay)

P_i = D(C_i) XOR C_{i-1}. Modifying C_{i-1}[15] changes P_i[15] without
touching D's correctness. The padding check answers 'does D(C_i) XOR your
crafted C_{i-1} end in a valid pad' — one bit per query, 256 queries per byte.

## CBC bit-flip

Same equation: C_{i-1}[j] XOR delta flips P_i[j] by delta while D(C_{i-1})
becomes unrelated garbage. One controlled block per sacrificed block.

## CTR/stream reuse

C = P XOR K(nonce). Same nonce → same K. C1 XOR C2 = P1 XOR P2: the key
cancels and natural-language redundancy reveals both texts under crib-drag.

## GCM nonce reuse

Tag = GHASH_H(AAD, CT) XOR E_K(nonce‖0x20). Two tags under one nonce XOR to
GHASH_H(CT1) XOR GHASH_H(CT2) — a polynomial equation in H. Solving it gives
the universal forgery key.

## Length extension

Merkle-Damgard: H(s||m) = CompressChain over padded s||m; the digest IS the
chaining state. Continue the chain with m' : H(s||m||glue||m') computable
without s.

## Single-byte XOR

C XOR k for k in 0..255; English-letter frequency picks k. Repeating-key:
recover period by Hamming distance, then per-column single-byte.
