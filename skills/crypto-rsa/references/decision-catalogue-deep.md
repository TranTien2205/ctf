# Decision catalogue deep — the if/else, fully annotated

## The count discriminant

```
if count(n) >= 2:
    if same_m and e_coprime and len(n) >= e:  → hastad
    if m2 == a*m1 + b:                        → franklin-reiter
    else:                                      → batch-gcd (gcd pairwise)
elif count(e) == 2 on 1 n and gcd(e1,e2)==1: → common-modulus
else:                                         → single-modulus
```

## The exponent discriminant

```
if e in (3,5,17,257):
    if m^e < n:     → small-e-root / nth-root
    if ≥e n's:      → hastad
elif e ≈ n (large): → wiener (d<n^.25) then boneh-durfee (d<n^.292)
elif gcd(e,phi)>1:  → eth-root
elif e==1:          → m=c
```

## The leak discriminant

```
if p_bits:            → coppersmith-high-bits / coppersmith-core
if d or phi or p,q:   → factor-from-d / rsa-decrypt
if dp,dq,qInv:        → crt manual (dp loop)
if sig+sig_faulty:    → crt manual (Bellcore gcd)
if m mod pi × several → crt residues
```

## The prime-shape discriminant

```
if |p-q| small (next_prime/p+k): → fermat
if p-1 smooth:                    → pollard-pm1
if n == p^2:                      → phi=p(p-1)
if n prime:                       → phi=n-1
if n smooth:                      → factorint → phi
```

## The verify

Every branch ends at `pow(m,e,n)==c` / `p*q==n`.
