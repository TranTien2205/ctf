# Skill status — the honest card

## The class

`crypto-prng` — predictable pseudorandom generator. **Catalogue** — no
`knowledge/chains/` card exists; nothing here has solved one.

## The corpus

A standard published-mechanism corpus + field procedure — NOT
locally-verified experience. Every attack is a real published mechanism
(LCG telescope gcd, Berlekamp-Massey, MT untemper, xorshift linear solve,
bounded-seed enumeration) applied through the real `crypto_attack.py`
ids and `xorshift128.py`.

## The tool coverage — verified against the real CLI

- `crypto_attack.py`: `lcg-recover`, `lcg-unknown-modulus`,
  `lcg-truncated`, `berlekamp-massey`, `lfsr-recover`, `lfsr-predict`,
  `mt19937-clone` — real ids, real flags.
- `tools/crypto/xorshift128.py` — the standalone `--outs --predict
  --selftest` CLI.
- `tools/crypto/{lcg,lfsr,mt19937,mt19937,xor,numtheory}.py` — library
  modules (no `__main__`); import only.

## The gates

`predict == held-back` — the accept. `predict != held` / `gcd→0` /
`L≈n/2` / `<count` — the falsifiers.

## The status rule

Never present this corpus as solved experience. Promote `catalogue` →
`verified` only on a real `classify_solve` → chain card → `field-notes`
`confirmed`.
