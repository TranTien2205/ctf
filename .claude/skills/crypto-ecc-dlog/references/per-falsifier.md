# Per-falsifier — each attack's kill condition, indexed

## `ecdsa-nonce-reuse` falsifier

No two `r` equal → dead. `d·G ≠ Q` after solve → `r`/`z`/`n` wrong.

## `hnp-ecdsa` falsifier

`d·G ≠ Q` after lattice → sigs too few / bound wrong / `k` unbiased.
Any `r` repeat → you're in the reuse case instead.

## `hnp` falsifier

No `d` reproducing `Q` → `B` too small, pairs too few, `(t,u)` derived wrong.

## `pohlig-hellman` falsifier

`smoothness` largest factor > 2⁴⁰ → PH dies in the largest factor.
`g^x ≠ h` → `order` wrong or `h ∉ <g>`.

## `bsgs` falsifier

`ord(g)`/bound > ~2⁴⁴ → table too big. No collision → `x` outside range.

## `smoothness` falsifier

Read-only — no falsifier itself; it *produces* the falsifier for PH.

## `smart_attack` falsifier

`#E ≠ p` → not anomalous. `x·P ≠ Q` → points/params wrong.

## `singular_ec` falsifier

`Δ ≠ 0 mod p` → not singular. `x·P ≠ Q` → wrong type/params.

## Invalid curve falsifier

Server validates point → impossible. `d` wrong post-CRT → bad `ord(P_i)`.

## The class falsifier

`x·G ≠ Q`/`g^x ≠ h` for every route → re-route entirely.
