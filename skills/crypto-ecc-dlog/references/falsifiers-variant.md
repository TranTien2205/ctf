# Falsifiers variant — the kill conditions, restated

## `ecdsa-nonce-reuse` kills

- No two sigs share `r` → reuse dead, `hnp-ecdsa` next.
- `d·G ≠ Q` → `z`/`order` wrong, not the attack.

## `hnp-ecdsa`/`hnp` kills

- `d·G ≠ Q` at `required` count + right `B` → bound/attack wrong.
- `k_i` not all `< B` → an outlier poisons the lattice.

## `pohlig-hellman` kills

- `smoothness` largest factor > 2⁴⁰ → PH out of reach.
- `g^x ≠ h` → `ord` wrong or `h ∉ <g>`.

## `bsgs` kills

- `ord`/`B` > 2⁴⁴ → out of reach.
- no match → `h ∉ <g>` or `x > B`.

## `smart`/`singular`/`invalid` kills

- `#E ≠ p` → not anomalous.
- `Δ ≠ 0` → not singular.
- `P` validated → invalid curve impossible.

## The class kill

- `x·G ≠ Q`/`g^x ≠ h` everywhere → wrong class entirely.
