# Evidence — what a solve counts as

## The standard

A classical solve counts when `enc(pt) == ct` and `pt` is language — the
transform reproduced the ciphertext. `flag{`/`CTF{` present is the flag.

## The candidates, not the confirms

- **a chi² minimum** — a *candidate* `k`; the decode is the confirm.
- **an `L` from Kasiski** — a candidate period; the coset-decode is the confirm.
- **an annealed `σ`** — a candidate until `σ(pt) == ct` and `pt` is language.
- **a near-decode** — `gLAG{...}` — a partially-right `σ`; the format positions
  reveal the wrong entries — polish, not a flag yet.

## The confirms

- **`k`/`L`/`σ`/depth/key** → `p = dec(c, param)` → **language** →
  `enc(p, param) == c` → confirmed.
- **`flag{`/`CTF{` present** → the flag.

## The `post-probe` record

`post-probe --hypothesis-id <h> --class crypto-classical --verdict confirms
--evidence-kind class --evidence "<the pt>" --response "<the decode output>"`

## The honest status

**Catalogue** — no local solve. `../field-notes.md` for real solves.
