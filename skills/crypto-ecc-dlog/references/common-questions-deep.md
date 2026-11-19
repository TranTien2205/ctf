# Common questions deep — the hard cases of the FAQ

## "Two `r` values *almost* equal — is that reuse?"

No — reuse means byte-identical `r` (identical `k`). Similar `r` is the
biased case → `hnp-ecdsa` with the bound on `k`'s range.

## "I have many sigs but the challenge says nothing about `k`"

Check the sig count: if it's ~`2·order_bits/leaked_bits` for some plausible
leak (e.g. ~64 for 8 bits on 256-bit), the challenge intends `hnp-ecdsa`.
Try `--nonce-bits` from the apparent `k` size (e.g. 128 for a "128-bit
nonce" hint).

## "`pohlig-hellman` returns `x` but `g^x ≠ h`"

The `--order` was wrong. Re-derive `ord(g)`: it's `p-1` for a generator,
else the subgroup order. `pow(h, order, p) == 1` confirms `h ∈ <g>`.

## "`bsgs` returns nothing"

`x` is outside the bound/order you supplied, or `h` isn't in `<g>`. If the
handout gave a bound, double-check it; else use `smoothness` to pick
`pohlig-hellman` or a defect route.

## "The challenge hands me `Q`, not `p, a, b`"

Then it's probably an ECDSA/nonce challenge, not a curve-defect one. The
`Q = d·G` verify still applies — the `G`/`n` are implied by the named curve.

## "What's `required_signatures` actually computing?"

`ceil(2·order_bits / leaked_bits)` — the count that makes the lattice
*information-theoretically* unique. Below it, LLL returns a wrong vector
that won't verify. `tools/crypto/hnp.py` exposes it.

## "Why does `crypto_attack.py` need `--sigs` as a file?"

A signature list can be large (dozens of hex values); a file is the only
sane way to pass it. The tool rejects inline JSON for `--sigs` by design —
it wants `[{"r","s","z"}]` or `[[r,s,z],…]`.
