# Field manual — the RSA engagement

`crypto_attack.py list` → the sheet → `attack-table.md` → `per-bound.md` →
`<id>` → `pow`/`p*q` → record.

Cheap first: `fermat`, `batch-gcd`, `small-e`, `common-modulus`, `pollard`,
`wiener`. Lattice last: `boneh-durfee`, `coppersmith`.

Traps: `e=3` needs `m³<n`; balanced primes ≠ close; count ≠ collision; a leak in
`m` ≠ a leak in `p`; a bound exceeded = negative; a public PEM = `n`,`e` only.

Record: `solved/` + `classify_solve.py` or `knowledge/attempts/`. See
`field-manual-deep.md`, `operator-notes.md`.
