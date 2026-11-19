# Multi-step chains deep — the solve sequences

## The chain anatomy

```
oracle → collect outputs → fingerprint → attack → verify → use → flag
```

Each arrow is a step with its own gate. The chain fails at the FIRST gate
that doesn't pass — never skip ahead.

## Chain 1 — LCG token prediction

```
GET /token (k+1 times) → o0..ok consecutive raw ints
→ fingerprint: difference gcd → affine → LCG
→ count ≥ 3
→ m known? → lcg-recover / m? → lcg-unknown-modulus
→ a,c[,m] → predict_next → verify held-back
→ forge the next token → authenticated endpoint → flag{
```

The long pole is normalization — most LCG challenges leak `x mod n` or a
float, and the fix is recognizing that BEFORE `lcg-recover`.

## Chain 2 — LFSR stream-ciphered flag

```
flag_ct + a known-plaintext prefix → keystream bits
→ berlekamp-massey → (width, taps)
→ lfsr-recover → register
→ lfsr-predict --count (flag_len*8) → keystream
→ ct ⊕ keystream → flag{
```

The known-plaintext is the entry — `flag{`/`CTF{` is a standard prefix
that yields the first keystream bits, which seed the BM recovery.

## Chain 3 — MT session-id prediction

```
GET /session (625 times) → 624 raw words + 1 held back
→ mt19937-clone --outputs o0..o623
→ predict_next == o624 → verify
→ predict_next → the admin's session id
→ hijack → flag{
```

The 624-collection is the whole cost. A challenge that caps collection
below 624 forces the seed-search branch instead.

## Chain 4 — seed-search token

```
issue a token + note the epoch → seed ∈ [issue-slack, now]
→ for ts in window: reproduce the token call
→ match → seed → predict next → flag{
```

The window bound is the whole skill — an `issued_at`/`iat`/`created`
field collapses a huge seed space to seconds.

## Chain 5 — truncated LCG keygen

```
GET /key (required+1 times) → h_i = x_i >> b leaks
→ m,a,c from source → lcg-truncated --low-bits b
→ state → predict_next → the key → decrypt → flag{
```

`java.util.Random`/`nextInt` is the canonical shape.

## The chain-choice rule

- **outputs ≥ 624 & raw words** → MT clone (Chain 3).
- **bitstream + known-plaintext** → LFSR (Chain 2).
- **a,b,c,m known + high-bit leak** → truncated LCG (Chain 5).
- **mod-m ints** → LCG (Chain 1).
- **small seed visible** → seed-search (Chain 4).

## The failure handoff

Any chain's verify step failing → `troubleshoot` → the falsifier →
`attempts` → `decide.py` picks the next rung (`reclassify`/
`writeup_search`/`novel_plan`/...). Never chain past a falsified verify.
