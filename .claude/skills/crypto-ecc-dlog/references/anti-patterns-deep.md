# Anti-patterns deep — the budget-wasting shapes, expanded

## The nonce-bound fishing

Trying `--nonce-bits` at 64, 96, 128, 160, 192 hoping one lands — the bound
comes from the *challenge statement* ("128-bit nonce", timestamp, leak size).
If unstated, infer from observed `k` magnitudes; don't brute-force `B`.

## The signature hoarding

Collecting 200 sigs for `hnp-ecdsa` when `required_signatures` says 8 —
more sigs make LLL *slower* (`m+1` dim pure-python) without helping.

## The wrong-tool churn

`bsgs` on a 200-bit order — the table never builds. `pohlig-hellman` on
`p-1 = 2q` — PH dies on `q`. `smart_attack` on `secp256k1` — `#E ≈ p` but
not equal. The gates exist to prevent this loop.

## The single-sig grind

One signature, rotating attacks — one sample carries zero nonce info.
Gather ≥2, or use the oracle.

## The verify-skip

Recording a scalar before `x·G == Q` — a plausible-looking `d` that doesn't
verify isn't a key, it's a wrong input.

## The curve-fixation

Solving ECDLP directly on a singular curve (expensive generic dlog) when
`singular_ec` maps to `Fp+`/`Fp*` in one step — check `Δ` first.

## The re-route blindness

Spending the whole budget on `hnp-ecdsa` when the challenge is actually
invalid-curve — the discriminator in `detection*.md` exists to prevent it.
