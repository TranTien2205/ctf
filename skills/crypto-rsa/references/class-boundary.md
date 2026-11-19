# Class boundary — what crypto-rsa is, and is not

## The class

RSA key or plaintext recovery — `n`,`e`,`c` + a leak → `p`,`q`,`d`,`φ`,`m`.
The violation is a weak `n`/`d`/`φ`/`m` relation — wrap, gap, divisor,
exponent, partial, relation/leak.

## What it is not

- **Not ECC/DH** — a curve, a `y = x^3+ax+b`, a `dLog`, a nonce, a
  `secp256k1`/`Curve25519` → `crypto-ecc-dlog`, not RSA.
- **Not a block/stream oracle** — AES/DES/a padding/bit-flip oracle →
  `crypto-symmetric-oracle`.
- **Not a PRNG** — a `state`/LCG/LFSR/`MT`/`xorshift` → `crypto-prng`.
- **Not classical** — a substitution/Vigenère/frequency → `crypto-classical`.
- **Not an encoding** — a base64/hex/carrier → `misc-encoding-carrier`.
- **Not a web layer** — a `pow`/`encrypt` inside a web service → the bug is in
  the web layer; `web-*` first.

## The boundary signals

| If you see | Route to |
|---|---|
| a `y`, `x`, `G`, `order`, `point`, `dlog` | `crypto-ecc-dlog` |
| AES/DES/block/ECB/CBC/CTR | `crypto-symmetric-oracle` |
| `random`, `state`, `LCG`, `LFSR`, `MT` | `crypto-prng` |
| a substitution/rot13/Vigenère/base | `crypto-classical`/`misc-encoding-carrier` |
| a `n`,`e`,`c` + a leak | **crypto-rsa** — this class |

## The verify

`pow(m,e,n)==c` / `p*q==n` — the RSA-shaped gate. A non-RSA problem fails it.
