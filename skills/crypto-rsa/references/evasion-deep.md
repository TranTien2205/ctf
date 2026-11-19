# Evasion deep — when the obvious shape hides the real bug

## The "everything looks standard" shape

`n`,`e`=65537,`c` — nothing obvious. The bug is *hidden* — a leak in a
side-file, a weak `keygen`, a shared `p` in a `.json`, a partial key. Read
*all* the artifacts before concluding "no violation".

## The disguised leak

- A `.json` field named `debug`/`hint`/`params` → a `d`/`phi`/`dp` leak.
- A `p`/`q`/`d`/`phi`/`dp`/`qInv` in a comment, a log, a partial private key.
- A redacted key → `coppersmith`/`crt`/`factor-from-d`.

## The multi-layer

- A `.pcap` → the handshake `n`,`e` and a `c` — then the RSA attack.
- A `keygen.py` that *looks* standard → grep the `next_prime`/`seed`/`e=3`.

## The decoy

- A flag-shaped `m` that fails `pow` — a wrong root (`eth-root`) or a decoy.
- A `m` that decrypts to garbage — strip the pad, try the other `g` roots.

## The strong-looking `n`

- `n` large/balanced → no `fermat`/`pollard-pm1` — but a `d`/`phi`/`dp`/`p`
  leak or `e`-weakness may still fire.
- `n` = `p²`/prime/multi — `factorint`/`isqrt` before concluding "hard".

## The honest status

Evasion here is *hiding* the bug, not evading a defense — the reads find it.
