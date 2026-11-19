# Decision table — the one-look router

## The table

```
─────────────────────────────────────────────────────────────
YOU HAVE                          →  RUN THIS                  BOUND
─────────────────────────────────────────────────────────────
d / phi / dp / p,q held           →  factor-from-d / rsa-decrypt  the value is real
≥2 moduli, same gen               →  batch-gcd                    a collision
same m, e coprime n               →  hastad                       ≥e n's, ∏n>m^e
1 n, 2 e, gcd(e1,e2)=1            →  common-modulus               gcd=1
p,q close (next_prime/p+k)        →  fermat                       |p-q| small
e~n, d<n^0.25                     →  wiener                       d<n^0.25
d<n^0.292                         →  boneh-durfee(-escalate)      d<n^0.292
p-bits / centred guess            →  coppersmith-high-bits/-core  window≥n^0.25
e=3, m^3<n                        →  small-e-root / nth-root      m^e<n
p-1 smooth                        →  pollard-pm1                  B≥largest factor
m2=a·m1+b                          →  franklin-reiter              linear, a,b known
residues / fault / dp,dq,qInv     →  crt                          ∏pi>m / fault / consistent
gcd(e,phi)>1, p,q held            →  eth-root                     the candidates
none of the above                 →  reclassify                   the class falsifier
─────────────────────────────────────────────────────────────
```

## The verify (every row)

`pow(m,e,n)==c` for `m` · `p*q==n` for `p`,`q` · `pow(c,d,n)==m` for `d`.

## The cost order

Cheap first: `factor-from-d`,`rsa-decrypt`,`eth-root`,`fermat`,`batch-gcd`,
`common-modulus`,`small-e-root`,`pollard-pm1`,`wiener`,`crt`,`franklin-reiter`,
`hastad`. Then the lattice: `boneh-durfee`,`coppersmith`.

## The honest status

Catalogue — published-standard. `../field-notes.md` records the real solves.
