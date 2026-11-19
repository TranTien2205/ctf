# Falsifiers deep — the kill conditions, expanded

## `ecdsa-nonce-reuse` falsifiers

- **No duplicate `r`** — nonce wasn't reused; move to `hnp-ecdsa` if `k` biased.
- **`d·G ≠ Q`** — `z` wrong (re-derive), `order` wrong, or `r` not equal.
- **One sig only** — no pair to subtract; needs ≥2.

## `hnp-ecdsa` falsifiers

- **`d·G ≠ Q` after lattice** — sigs too few, bound wrong, or `k` unbiased.
- **Any `r` repeats** — the pair belongs to `ecdsa-nonce-reuse`.
- **LLL returns junk** — `B` undersized or an outlier `k_i` in the set.

## `pohlig-hellman` falsifiers

- **`smoothness` largest factor > 2⁴⁰** — PH dies in that factor.
- **`g^x ≠ h`** — `ord(g)` wrong or `h ∉ <g>`.
- **Safe-prime order** — `p-1 = 2q`, `q` large — designed-resistant.

## `bsgs` falsifiers

- **`ord`/`B` > 2⁴⁴** — table too big.
- **No collision** — `x` outside range or `h ∉ <g>`.

## `smart_attack` falsifiers

- **`#E ≠ p`** — not anomalous.
- **`x·P ≠ Q`** — params/points wrong.

## `singular_ec` falsifiers

- **`Δ ≠ 0 mod p`** — not singular.
- **`x·P ≠ Q`** — cusp/node misidentified or wrong params.

## Invalid curve falsifiers

- **Server validates `P`** — impossible; the check is the bug's whole existence.
- **`d` wrong post-CRT** — `ord(P'_i)` miscounted.

## The class falsifier

Every route fails `x·G == Q`/`g^x == h` → this wasn't an ECC/DLog challenge
at all — re-route.
