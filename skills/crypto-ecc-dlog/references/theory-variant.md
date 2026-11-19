# Theory variant — the math from the tool's side

## `hnp.py`

`ecdsa_recover_nonce_reuse(sig_a, sig_b, order)` — closed-form `d`.
`ecdsa_recover_biased_nonce(sigs, order, nonce_bits|nonce_bound, curve, pubkey)`
— builds `L`, `lll_reduce`, scans candidates.
`hnp_solve(t_list, u_list, modulus, bound)` — the raw lattice.
`required_signatures(order_bits, nonce_bits)` — `⌈2·order_bits/leaked_bits⌉`.

## `dlog.py`

`pohlig_hellman(g, h, p, order)` — per-factor BSGS + CRT; computes `ord(g)`
first so a non-generator doesn't yield a wrong coset.
`bsgs(g, h, p, order, max_table=1<<22)` — table `j→g·g^j`, giant `h·g^{-im}`.

## `smart_attack.py`

p-adic lift of `E` and `P, Q` to `Q_p`; `λ(Q')/λ(P')` mod `p` is `x`.

## `singular_ec.py`

Maps to `Fp+` (cusp) or `Fp*` (node); the ECDLP becomes `slope(Q)/slope(P)`
or a standard `pohlig-hellman`/`bsgs` on `p-1`.

## `ec.py`

`ec.curve("name" | {"p","a","b"})` → `point`, `add`, `mul`, `order` (small `p`).

## `lll.py`

Pure-python LLL — no `fpylll` here; keep `m` near `required_signatures`.

## The bound math

`m ≥ order_bits / log2(n/B)` — the count that makes the lattice unique.
`B = 2^{nonce_bits}` or `--nonce-bound` integer.
