# Operator checklist — the run card, every line

## Setup

- [ ] `selfcheck.py` green.
- [ ] `crypto_attack.py list` — ids present.
- [ ] `xorshift128.py --selftest` green.
- [ ] class is `crypto-prng`, not the confusables.

## Recon

- [ ] generator fingerprinted — name or gcd/BM/clone.
- [ ] `urandom`/`secrets`/`crypto.`/`SecureRandom` ruled OUT.
- [ ] outputs collected — consecutive, raw.
- [ ] shape noted — int/hex/float/bit/`mod n`/`>>b`.
- [ ] seed/`iat`/params visible — `m`/`a`,`c`/taps/`low-bits`/window.

## Gate

- [ ] count meets floor — 3/6/req/2w/624/4.
- [ ] outputs normalized — raw ints.
- [ ] aligned — no gaps, no reseed.
- [ ] params identified.

## Solve

- [ ] attack picked — the params-known column.
- [ ] command real flags.
- [ ] held-back output reserved.

## Close

- [ ] `predict == held-back` — bit-for-bit.
- [ ] flag-object used — forged/decrypted/won.
- [ ] `flag{`/`CTF{` from response/artifact.
- [ ] `post-probe`/`pre-flag` — evidence substring of response.
- [ ] `attempts`/`classify_solve`/`field-notes`.
