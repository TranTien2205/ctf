# Negative results catalogue — the closing observations, indexed

## The `gcd` negatives

- `gcd(ni,nj)=1` all pairs → `batch-gcd` closed.
- `gcd(e1,e2)>1` → `common-modulus` gives `m^gcd`.
- `gcd(a^{B!}-1,n)=1` → `pollard-pm1` at `B` closed.
- `gcd(s'^e-m,n)=1` → `crt` Bellcore closed.
- `gcd(e·dp-1,...)≠` factor → `crt` dp closed.

## The bound negatives

- `d ≥ n^0.25` → `wiener` closed → `boneh-durfee`.
- `d ≥ n^0.292` → small-`d` fully closed.
- window `< n^0.25`/`n^(1/e)` → `coppersmith` closed.
- `m^e ≥ n` → `small-e-root`/`nth-root` closed.
- `<e` n's / `∏n<m^e` / pad → `hastad` closed.
- `|p-q|` too large → `fermat` closed.
- `p-1` not `B`-smooth → `pollard-pm1` closed.
- relation not `a·m1+b` → `franklin-reiter` closed.
- `∏pi≤m`/no fault/inconsistent `dp` → `crt` closed.
- `gcd(e,phi)=1` → `eth-root` closed (normal `inverse`).

## The class negative

Every bound on the sheet met → **no RSA violation** → reclassify —
`crypto-symmetric-oracle`, `crypto-ecc-dlog`, `crypto-prng`, or `web-*`.

## The record

`knowledge/attempts/<challenge>.json` + `negative-results.md` +
`../field-notes.md`. A negative is evidence — the precondition that would reopen
it is the value.
