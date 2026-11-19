# Quick reference — the RSA card

`crypto_attack.py list` → `attack-table.md` → bound → attack → `pow`/`p*q` verify.

```
d/phi/dp/p,q → factor-from-d/rsa-decrypt/eth-root
≥2 moduli     → batch-gcd
same m,e n's  → hastad
2 e on 1 n    → common-modulus
p,q close     → fermat
e~n           → wiener→boneh-durfee
p-bits        → coppersmith
e=3,m short   → small-e-root
p-1 smooth    → pollard-pm1
m2=a·m1+b     → franklin-reiter
residues/fault→ crt
gcd(e,phi)>1  → eth-root
```

Bounds: `d<n^0.25`/`0.292`, window`n^0.25`, `m^e<n`, `≥e` n's, `gcd=1`,
`|p-q|`,`B`,`∏pi>m`,linear,`gcd(e,phi)>1`.

Catalogue class. See `quick-reference-deep.md`.
