# Field manual deep — the procedures, annotated

## The discriminate procedure

1. `crypto_attack.py list` — the inventory + `lll_backend`.
2. `parameter-sheet.md` — `n`,`e`,`c`,counts,`e_sig`,leak,keygen,degenerate.
3. `attack-table.md` — the first-yes row.
4. `per-bound.md` — the falsifier read.

## The cheap-attack procedure

`fermat` → `batch-gcd` → `small-e-root` → `common-modulus` → `pollard-pm1` →
`wiener` → `crt`/`hastad`/`factor-from-d`/`rsa-decrypt`/`eth-root` — the
non-lattice ids, in cost order.

## The lattice procedure

`boneh-durfee` (`d<n^0.292`) → `boneh-durfee-escalate` (`m`,`t` up) →
`coppersmith-high-bits`/`coppersmith-core` (bits) — give the budget, approach
the bound.

## The manual procedure

`franklin-reiter` (`tools/crypto/franklin_reiter.py`) · `crt` Bellcore `gcd` ·
`crt` `dp`/`dq`/`qInv` loop — no `crypto_attack.py` id.

## The verify procedure

`m` → `pow(m,e,n)==c` → `long_to_bytes(m)` → strip a pad → the flag bytes.
`p`,`q` → `p*q==n` → `phi` → `d` → `m` → `pow`.

## The chain procedure

`factor`/`d`/`phi` → `factor-from-d`/`rsa-decrypt --p --q` → `m` → `pow` →
the flag.
