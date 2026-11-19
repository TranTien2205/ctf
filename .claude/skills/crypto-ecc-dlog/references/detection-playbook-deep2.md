# Detection playbook deep 2 — the branches with the why

## The nonce branch — why `r` first

`r` equality is O(1) and unambiguous — a reused `k` collapses the lattice
need entirely. The bound/`(t,u)` reads are more expensive and only pay
when `r`s are distinct.

## The dlog branch — why `smoothness` first

`smoothness --n ord` is the cheapest discriminator between PH (`ord`
smooth) and BSGS (`x` bounded) and neither (safe-prime). The two attacks
are both more expensive than the gate.

## The defect branch — why `Δ` first

`Δ == 0` is one modular computation; `#E` needs a count; validation needs
an oracle probe. Cheapest gate first, and `Δ`/`#E` kills generic dlog
intents early.

## The close branch — why verify before record

A scalar that doesn't verify isn't evidence — `post-probe` would record a
false claim. `x·G == Q`/`pow == h` is the only accept; `flag{` is the
impact.
