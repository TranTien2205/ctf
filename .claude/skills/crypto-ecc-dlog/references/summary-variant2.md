# Summary variant 2 — the corpus in one page, alternate

## The three families

- **nonce** — `ecdsa-nonce-reuse` / `hnp-ecdsa` / `hnp`. The `r`-dedupe gate
  separates the closed form from the lattice.
- **dlog** — `pohlig-hellman` / `bsgs` / `smoothness` (the gate). Smooth
  order vs bounded exponent.
- **curve-defect** — `smart_attack` / `singular_ec` / invalid curve
  (`ec.py` + `bsgs`/`pohlig` + CRT). `Δ`/`#E`/validation gates.

## The attack ids

`ecdsa-nonce-reuse` `hnp-ecdsa` `hnp` `pohlig-hellman` `bsgs`
`smoothness` + `smart_attack.py` `singular_ec.py` `ec.py`.

## The gates in order

`r` dedupe → `k` bound → `smoothness` → `x` bound → `Δ`/`#E`/validation →
solve → verify → record.

## The bounds

`bsgs ≤ 2^44` · `PH ≤ 2^40` · `m ≥ 2·order_bits/leaked` · `Δ == 0` ·
`#E == p` · `--order = n` · `--sigs` = FILE.

## The proof + the status

`x·G == Q`/`pow == h` + `flag{`; catalogue, no local chains.
