# Mechanism variant — the primitives per family

## Nonce family

- `k` identical across 2 sigs → closed-form `d` — `hnp.ecdsa_recover_nonce_reuse`.
- `k_i < B` across m sigs → lattice → `hnp.ecdsa_recover_biased_nonce`.
- `(t,u)` pairs → `hnp.hnp_solve`.

## Dlog family

- `ord` smooth → `dlog.pohlig_hellman` — per-factor + CRT.
- `x` bounded → `dlog.bsgs` — `O(√B)` time+space.
- `ord` unknown → `numtheory.smoothness` → gate.

## Defect family

- `#E == p` → `smart_attack` — p-adic lift, linear.
- `Δ == 0` → `singular_ec` — `Fp+`/`Fp*` isomorphism.
- unvalidated point → `ec.py` fake-curve + `bsgs`/`pohlig` per factor, CRT.

## The verify primitive

`E.mul(G, d) == E.point(*Q)` or `pow(g, x, p) == h` — same everywhere.

## The `--sigs` primitive

JSON file `[{"r","s","z"}]` — `r`/`s`/`z` ints or hex strings; `z` = hash
as integer.

## The lattice primitive

`lll.lll_reduce` on the `(m+1)`-dim HNP lattice — pure-python, keep `m` small.
