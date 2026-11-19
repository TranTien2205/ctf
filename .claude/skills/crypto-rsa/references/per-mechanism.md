# Per-mechanism map — the primitive → the falsifier

## wrap

- **Attacks**: `small-e-root`, `nth-root`, `hastad`.
- **Falsifier**: `m^e ≥ n` (root) or `<e` n's / `∏ni<m^e` / a pad (`hastad`).

## gap

- **Attack**: `fermat`.
- **Falsifier**: `|p-q|` too large — `a` walks past the budget.

## divisor

- **Attacks**: `batch-gcd`, `pollard-pm1`.
- **Falsifier**: all `gcd(ni,nj)=1` / `p-1` not `B`-smooth.

## exponent

- **Attacks**: `common-modulus`, `wiener`, `boneh-durfee`, `factor-from-d`.
- **Falsifier**: `gcd(e1,e2)>1` / `d≥n^0.25` / `d≥n^0.292` / `d` fails `pow`.

## partial

- **Attacks**: `coppersmith-high-bits`, `coppersmith-core`, partial-message.
- **Falsifier**: unknown window `< n^0.25` (factor) / `< n^(1/e)` (message).

## relation

- **Attacks**: `franklin-reiter`, `crt`.
- **Falsifier**: relation not linear / `∏pi≤m` / no fault.

## leak

- **Attacks**: `factor-from-d`, `crt`, `rsa-decrypt`, `eth-root`.
- **Falsifier**: the leaked value fails `pow`/`gcd` — wrong input.

## The rule

A mechanism's falsifier is binary — observed = the family closed for this
challenge. Record it; do not retry the bound.
