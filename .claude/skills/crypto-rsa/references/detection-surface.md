# Detection surface — every place the signal can hide

## The file surface

- **`keygen.py` / `chal.py` / `output.txt`** — the generator and the numbers.
  The comment names the misuse; the numbers feed the sheet.
- **`pubkey.pem` / `cert.crt`** — a public `n`,`e`. `openssl x509 -text` or
  `RSA.importKey`. `n`,`e` only — the rest is on the sheet.
- **`priv.pem`** — a *full* private key ends it; a **partial** (redacted) one is
  the `coppersmith`/`crt`/`factor-from-d` leak.
- **`keys.json` / `moduli.txt`** — the batch for `batch-gcd` / `hastad`.
- **`flag.txt.enc` / `output.bin`** — the `c`.

## The runtime surface

- **a socket printing `n`,`e`,`c`** — transport, not an oracle. Treat as the
  numbers. If it *re-encrypts* your `m` → `crypto-symmetric-oracle`.
- **a signature service** — returns `(n, e, sig)` or `(n, e, sig, sig_faulty)`.
  The pair → `crt` Bellcore.
- **an interactive `oracle.py`** — a menu that encrypts/decrypts/signs →
  `crypto-symmetric-oracle`, not this class.

## The numeric surface

- **`e` small** (3/5/17) → wrap / broadcast / relation.
- **`e` large** (~`n`) → small `d` → wiener / boneh-durfee.
- **`n` even / prime / square / smooth** → degenerate.
- **`c` < `n`** → `m^e` wrapped — not a root.

## The leak surface

- `d` / `phi` / `dp` / `dq` / `qInv` → arithmetic.
- `p`'s high/low bits → `coppersmith`.
- `m`'s partial → `coppersmith` partial-message.
- a fault → `crt` Bellcore.
- `p`,`q` → `rsa-decrypt` / `eth-root`.

## The read-order

`recon-order.md` — source → count → exponent → leak → relation. The first yes
picks the attack.
