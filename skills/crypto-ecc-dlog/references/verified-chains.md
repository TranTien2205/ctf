# Verified chains — the honest status

## Status: catalogue

No chain card in this repository has solved a `crypto-ecc-dlog` challenge.
The corpus is standard published knowledge shaped for the toolkit's tools —
record what actually happens in `../field-notes.md` on the first real solve.

## What a verified card would carry

- The curve/group params (`p`, `a`, `b`, `G`, `n`).
- The attack id that landed (`ecdsa-nonce-reuse`/`hnp-ecdsa`/`pohlig-hellman`/
  `bsgs`/`smart_attack`/`singular_ec`/invalid-curve).
- The `--sigs`/`--order`/`--nonce-*` inputs that worked.
- The falsifier that would have saved the first attempt.
- The verify transcript (`x·G == Q`).

## The chains the class covers

- `sign → reuse → d → forge` — `ecdsa-nonce-reuse` → token forgery.
- `oracle → biased k → d → sign` — `hnp-ecdsa` → `d`.
- `dlog → x → shared secret → decrypt` — `pohlig-hellman`/`bsgs`.
- `defect → x → decrypt` — `smart_attack`/`singular_ec`.
- `point oracle → fake curve → CRT` — invalid curve.

## The verify gate

`x·G == Q`/`g^x == h` is the only completion — everything before it is
candidate work.
