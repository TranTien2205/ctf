# Common mistakes deep — the subtle traps

## The `r`-equality trap

`r` must be *identical* — `r_i == r_j`, not `r_i ≈ r_j`. A "close" `r`
(differing in a few bits) means `k` differed — that's `hnp-ecdsa` territory,
not reuse.

## The `z` trap

`z` is the *truncated* hash, not the whole hash and not `mod n` (usually).
A `d` that recovers but fails verify is almost always a wrong `z` — try
the other convention before declaring the attack dead.

## The `order` trap

- `--order` = `n` — the subgroup order, not `p`.
- On curves: `n` = `ord(G)`, not `#E` unless `G` generates all of `E`.
- On fields: `ord(g)`, which may be `p-1` (generator) or a factor of it.

## The count trap

`hnp-ecdsa` with too few sigs returns a wrong `d` that fails verify — the
error looks like a math bug but it's an information deficit. Add sigs.

## The bound trap

`--nonce-bound`/`--nonce-bits` must *cover* the true `k`. An under-bound
fails silently; an over-bound wastes the lattice. The challenge statement
("128-bit", "timestamp", "8-bit leak") is the source of truth.

## The curve trap

`ec.curve` needs `{"p","a","b"}` — `G`, `Q`, `n` are points/orders, not
curve params. Passing `n` where `p` belongs silently produces a wrong field.

## The verify trap

`d` from the attack is a *candidate* — `d·G == Q` decides. A scalar that
doesn't reproduce the public key is not the key; record the fail, don't
claim the flag.
