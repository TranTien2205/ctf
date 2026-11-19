# Per-condition map — the precondition → the attack

## The wrap conditions

- `m^e < n` → `small-e-root`, `nth-root`.
- same `m`, `e` coprime `n`, `∏ni>m^e` → `hastad`.

## The close-prime conditions

- `|p-q|` small (`next_prime`,`p+k`,`q=p+2`,shared seed) → `fermat`.

## The shared-divisor conditions

- a prime reused across `n_i`,`n_j` → `batch-gcd`.
- `p-1` `B`-smooth → `pollard-pm1`.

## The exponent conditions

- `d < n^0.25` → `wiener`.
- `d < n^0.292` → `boneh-durfee`.
- `gcd(e1,e2)=1`, two `c` of same `m` → `common-modulus`.
- `d`/`phi`/`dp` held → `factor-from-d`/`crt`/`rsa-decrypt`.
- `gcd(e,phi)>1` → `eth-root`.

## The partial-knowledge conditions

- `p` top `n/2` bits known → `coppersmith-high-bits`.
- `|x|<n^0.25` unknown window → `coppersmith-core`.
- `m` partial, `|x|<n^(1/e)` → `coppersmith` partial-message.

## The relation conditions

- `m2=a·m1+b` linear, `a`,`b` known → `franklin-reiter`.
- `m` residues mod `pi`, `∏pi>m` → `crt`.
- a faulty+correct `sig` of same `m` → `crt` Bellcore.
- `dp`,`dq`,`qInv` consistent → `crt`.

## The degenerate conditions

- `n=p²` → `phi=p(p-1)`.
- `n` prime → `phi=n-1`.
- `n=p·q·r` → `phi=∏(pi-1)`.
- `e`=1 / `m`=0,1 → trivial.

## The falsifier = the negated condition

Every condition's negation is the falsifier — `d≥n^0.292`, window `<n^0.25`,
`m^e≥n`, `<e` n's, `gcd>1`, `|p-q|` large, `p-1` not smooth, no fault, no leak.
A condition unmet = the attack closed.
