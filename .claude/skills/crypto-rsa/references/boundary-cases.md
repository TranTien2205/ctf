# Boundary cases — where the bound sits, and which side is live

## The small-d boundary

- `d < n^0.25` → `wiener` live.
- `n^0.25 ≤ d < n^0.292` → `boneh-durfee` live, `wiener` dead.
- `d ≥ n^0.292` → small-d dead.

## The Coppersmith boundary

- unknown `≥ n^0.25` → `coppersmith-*` live.
- unknown `< n^0.25` → dead — the leak is too small.
- For a partial *message*: `|x| < n^(1/e)` — different bound.

## The wrap boundary

- `m^e < n` → `small-e-root`/`nth-root`/`hastad` live.
- `m^e ≥ n` → wrapped → `hastad`/`coppersmith`, never a plain root.

## The broadcast boundary

- `≥e` coprime `n`, `∏ni>m^e`, no pad → `hastad` live.
- `<e` n's / `∏ni<m^e` / a pad → dead → `coppersmith`/`franklin-reiter`.

## The common-modulus boundary

- `gcd(e1,e2)=1` → live.
- `gcd>1` → `m^gcd`, not `m` — `nth-root` if `m^gcd<n`.

## The fermat boundary

- `|p-q|` small (`a` converges in budget) → live.
- `|p-q|` large → dead → `pollard-pm1`/a leak.

## The pollard boundary

- `p-1` `B`-smooth, `B`≥largest factor → live.
- `p-1` with a factor `>B` → dead at that `B` — raise `B` or closed.

## The crt boundary

- `∏pi>m` / a fault / consistent `dp`,`dq`,`qInv` → live.
- `∏pi≤m` / no fault / inconsistent → dead.

## The eth-root boundary

- `gcd(e,phi)>1`, `p`,`q` held → live.
- `gcd=1` → normal `inverse` — `rsa-decrypt`, not `eth-root`.

## The class boundary

Every bound met → no RSA violation → `class-boundary.md` / the neighbours.
