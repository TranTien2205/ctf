# Class boundary — what's crypto-classical, what's not

## Inside

- `caesar`, `ROT13`, `ROT5/18/47`, `atbash` — the shifts/reflections.
- `subst`, `affine`, keyword — the monoalphabetic `σ`.
- `vigenere`, `beaufort`, `autokey`, `gronsfeld` — the polyalphabetic.
- `railfence`, `columnar`, `route`, `scytale` — the transposition `π`.
- `playfair`, `polybius`, `baconian`, `adfgx`, `hill` — the named others.

## Outside — the boundaries

- **`misc-encoding-carrier`** — a `+/=`/hex/`01`/`.-` `ct` — an *encoding*, no
  key, `enc_detect` — not a cipher.
- **`crypto-symmetric-oracle`** — a *block/stream* cipher oracle — DES/AES/RC4,
  padding oracle, ECB cut-and-paste — a *modern* cipher, not a letter-`σ`.
- **`crypto-prng`** — an `LCG`/`LFSR`/MT state — a *stream of numbers*, not a
  letter transform.
- **`crypto-rsa`/`crypto-ecc-dlog`** — asymmetric — `N`,`e`,`p`,`q`/`G`,`P`,`n`.

## The boundary rule

The *charset* decides — letters-only letter-transform → classical; a structured
alphabet → encoding; a `mod`/`big-int`/`curve` → a modern class.
