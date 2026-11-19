# Per-boundary deep — the class-boundary entries, annotated

## `misc-encoding-carrier` — the encoding boundary

- **Out**: a `+/=`/hex/`01`/`.-`/`ADFGVX` `ct` — `enc_detect.py` decodes it
  directly; no key.
- **In**: a letters-only `ct` the decoder is *for* — `cipher_id` then
  `classical_solve`.
- **The boundary**: the *charset*, not the length — `enc_detect` first; a
  `base64` blob annealed as `subst` is a wasted probe.

## `crypto-symmetric-oracle` — the modern-cipher boundary

- **Out**: a block/stream oracle — DES/AES/RC4, padding oracle, ECB
  cut-and-paste, CTR-bitflip — `crypto_attack.py` — a *modern* cipher with a
  `mod`/`block`/`oracle`/`key`/`iv` vocabulary.
- **In**: a letter-`σ`/`k`/`π` — the statistics apply.
- **The boundary**: `mod`/`block`/`oracle`/`iv` → modern; letters-only →
  classical.

## `crypto-prng` — the PRNG boundary

- **Out**: an `LCG`/`LFSR`/MT/`random` state — `crypto_attack.py` — a *number*
  stream (`seed`,`mod`,`tap`,`temper`).
- **In**: a letter transform — the statistics apply.
- **The boundary**: a `state`/`seed`/`mod`/`tap`/`temper` vocabulary.

## `crypto-rsa`/`crypto-ecc-dlog` — the asymmetric boundary

- **Out**: `N`,`e`,`p`,`q`/`G`,`P`,`n`,`d` — `crypto_attack.py` — asymmetric.
- **In**: a letter-`σ`/`k`/`π` — symmetric, classical.
- **The boundary**: a `mod`-int/`curve`/`public-key` vocabulary.

## The boundary rule

The *charset* decides — a letter-only letter-transform → `crypto-classical`;
a structured alphabet → `misc-encoding-carrier`; a `mod`/`big-int`/`curve` →
a modern class (`crypto-symmetric-oracle`/`prng`/`rsa`/`ecc-dlog`).
