# Probe order deep — cheapest first, annotated

## Why the order matters

`decide.py` budgets 5 probes/15 min per mechanism — spend the cheapest
reads first so the expensive attack only runs when it's warranted.

## The read order

1. **Parse** — extract the artifact; free.
2. **`r` dedupe** — `Counter(r)` — O(1), the first nonce gate.
3. **`z` convention** — free, decides every nonce attack's input.
4. **`smoothness --n ord`** — a few divisions — gates the whole dlog family.
5. **`Δ`/`#E`** — modular arithmetic/counting — gates the defect family.
6. **bound reads** — `k` bound, `x` bound — free if stated.
7. **`required_signatures`** — a division — the lattice feasibility.
8. **validation probe** — one oracle call — gates invalid curve.

## The attack order (per family)

- nonce: `ecdsa-nonce-reuse` (closed form) → `hnp-ecdsa`/`hnp` (lattice).
- dlog: `pohlig-hellman` (smooth) vs `bsgs` (bounded) — `smoothness` decides.
- defect: `singular` (Δ) → `smart` (#E) → invalid curve (validation).

## The verify — always last

`x·G == Q`/`pow == h` — cheap, mandatory.
