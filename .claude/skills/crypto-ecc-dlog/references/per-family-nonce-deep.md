# Per-family nonce deep — the nonce family, expanded

## The three attacks

| Attack | Trigger | Files |
|---|---|---|
| `ecdsa-nonce-reuse` | `r_i == r_j` | `per-attack-ecdsa-nonce-reuse.md`,`ecdsa-nonce-reuse-deep.md` |
| `hnp-ecdsa` | `k_i < B`, `r`s distinct | `per-attack-hnp-ecdsa.md`,`hnp-ecdsa-deep.md` |
| `hnp` | `(t,u)` leaked | `per-attack-hnp.md`,`hnp-deep.md` |

## The discriminator — the order matters

1. `r` dedupe FIRST — reuse is closed-form, no lattice.
2. distinct `r` + `k` bound → `hnp-ecdsa`.
3. distinct `r` + partial `k` (`t,u`) → `hnp`.

Never open the lattice before the dedupe — reuse makes it unnecessary.

## The `--order` = `n` invariant

Every nonce attack takes `--order <n>` — the subgroup order `ord(G)`, never
the field prime `p`. The single highest-frequency trap.

## The `--sigs` = FILE invariant

Every sig-taking attack wants a JSON **file**, not inline JSON.

## The verify

`d·G == Q` on the real curve — the only accept for `d`.
