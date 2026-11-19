# Per-bound map — the bound → the attacks → the falsifier

## `d < n^0.25`

- Attacks: `wiener`.
- Falsifier: `d ≥ n^0.25` → escalate to `boneh-durfee`.

## `d < n^0.292`

- Attacks: `boneh-durfee`, `boneh-durfee-escalate`.
- Falsifier: `d ≥ n^0.292` → small-d closed; look for a leak or another class.

## unknown `< n^0.25`

- Attacks: `coppersmith-high-bits`, `coppersmith-core` (β=½).
- Falsifier: window `< n^0.25` → need a bigger leak; partial-message is `n^(1/e)`.

## `m^e < n`

- Attacks: `small-e-root`, `nth-root`.
- Falsifier: `m^e ≥ n` → wrapped → `hastad`/`coppersmith`.

## `≥ e` coprime `n`, `∏ni > m^e`

- Attack: `hastad`.
- Falsifier: `<e` n's / `∏ni<m^e` / a pad.

## `gcd(e1,e2)=1`

- Attack: `common-modulus`.
- Falsifier: `gcd>1` → `m^gcd`, then `nth-root` if `m^gcd<n`.

## `|p-q|` small

- Attack: `fermat`.
- Falsifier: `a` past the budget → `|p-q|` too large.

## `B` ≥ largest `p-1` factor

- Attack: `pollard-pm1`.
- Falsifier: `gcd(a^{B!}-1,n)=1` → `p-1` not `B`-smooth.

## `m2 = a·m1+b` linear

- Attack: `franklin-reiter`.
- Falsifier: relation not linear.

## `∏pi > m` / a fault / consistent `dp`,`dq`,`qInv`

- Attack: `crt`.
- Falsifier: `∏pi≤m` / no fault / inconsistent.

## `gcd(e,phi)>1`, `p`,`q` held

- Attack: `eth-root`.
- Falsifier: `gcd=1` → normal `inverse`.

## `d`/`phi`/`p`,`q` held

- Attacks: `factor-from-d`, `rsa-decrypt`.
- Falsifier: the value fails `pow`/`p*q` — wrong input.
