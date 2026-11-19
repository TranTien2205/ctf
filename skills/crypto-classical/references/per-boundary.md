# Per-boundary — the class-boundary entries, one each

## `misc-encoding-carrier` — the encoding boundary

- **Out**: a `+/=`/hex/`01`/`.-` `ct` — `enc_detect.py` decodes it directly.
- **In**: a letters-only `ct` the decoder is *for* — `cipher_id` then
  `classical_solve`.
- **The boundary**: the charset, not the length — `enc_detect` first.

## `crypto-symmetric-oracle` — the modern-cipher boundary

- **Out**: a block/stream oracle — DES/AES/RC4, padding oracle, ECB
  cut-and-paste, CTR-bitflip — `crypto_attack.py`.
- **In**: a letter-`σ`/`k`/`π` — the statistics apply.
- **The boundary**: a `mod`/`block`/`oracle`/`key`/`iv` vs a letter-only `ct`.

## `crypto-prng` — the PRNG boundary

- **Out**: an `LCG`/`LFSR`/MT/`random` state — `crypto_attack.py` — a *number*
  stream.
- **In**: a letter transform — the statistics apply.
- **The boundary**: a `state`/`seed`/`mod`/`tap`/`temper` vocabulary.

## `crypto-rsa`/`crypto-ecc-dlog` — the asymmetric boundary

- **Out**: `N`,`e`,`p`,`q`/`G`,`P`,`n`,`d` — `crypto_attack.py`.
- **In**: a letter-`σ`/`k`/`π`.
- **The boundary**: a `mod`-int/`curve`/`key` vocabulary.

## The boundary rule

The charset decides — a letter-only letter-transform → `crypto-classical`; a
structured alphabet → encoding; a `mod`/`big-int`/`curve` → a modern class.
