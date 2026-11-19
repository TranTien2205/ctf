# Theory map — the bound → the classes it bounds

## The bound table, grouped

| Bound | Attacks it bounds |
|---|---|
| `d < n^0.25` | `wiener` |
| `d < n^0.292` | `boneh-durfee`, `boneh-durfee-escalate` |
| unknown `< n^0.25` | `coppersmith-high-bits`, `coppersmith-core` |
| `m^e < n` | `small-e-root`, `nth-root` |
| `≥ e` moduli, `∏n>m^e` | `hastad` |
| `gcd(e1,e2)=1` | `common-modulus` |
| `|p-q|` small | `fermat` |
| `B` ≥ largest `p-1` factor | `pollard-pm1` |
| linear `m2=a·m1+b` | `franklin_reiter` |
| `∏pi>m` / a fault / `dp` | `crt` |
| `gcd(e,phi)`>1 / factors held | `eth-root`/`rsa-decrypt`/`factor-from-d` |

## The bound hierarchy

```
d < n^0.25            → wiener          (CF, deterministic, cheap)
d < n^0.292           → boneh-durfee    (lattice, the real ceiling)
d ≥ n^0.292           → small-d dead    (the falsifier)

window ≥ n^0.25       → coppersmith     (factor recovery)
window < n^0.25       → coppersmith dead

m^e < n               → exact root      (small-e-root)
m^e ≥ n, e recipients → hastad          (CRT+root)
m^e ≥ n, partial m    → coppersmith     (message recovery)
```

## The bound the theory enforces

Every bound is a theorem — LLL's approximation factor limits the recoverable
size. A bound exceeded is a falsifier, not a tuning problem. The `m`/`t` lattice
parameters approach the bound; they cannot exceed it.

## The non-bounded attacks

`factor-from-d`, `rsa-decrypt`, `eth-root`, `common-modulus` (given `gcd=1`),
`fermat` (given small gap), `batch-gcd` (given a collision), `pollard-pm1`
(given smoothness) — these are *arithmetic*, not lattice, so their "bound" is a
yes/no precondition, not a size limit.
