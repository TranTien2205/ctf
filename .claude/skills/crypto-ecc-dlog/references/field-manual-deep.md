# Field manual deep — the expanded 15-minute card

## The group read

```
p   field prime               a,b curve coeffs (y² = x³ + ax + b)
G   generator (ord = n)       n   subgroup order  ← --order is THIS
Q   d·G public                sigs  [{"r","s","z"}] file
```

## The gates

```
r dup? → ecdsa-nonce-reuse --sigs f --order n
k < B? → hnp-ecdsa --sigs f --order n --nonce-bits B
(t,u)? → hnp --t f --u f --modulus n --bound B
ord smooth? → pohlig-hellman --g --h --p --order n
x bounded? → bsgs --g --h --p --order B
ord ? → smoothness --n n
#E == p? → smart_attack.py
Δ == 0? → singular_ec.py
unvalidated P? → invalid curve (ec.py + bsgs/pohlig + CRT)
```

## The bounds

```
bsgs ord ≤ 2^44          PH largest factor ≤ 2^40
m ≥ 2·order_bits/leaked  Δ exact 0      #E exact p
B covers all k           --order = n    --sigs = FILE
```

## The verify

```
E.mul(G, d) == E.point(*Q)     pow(g, x, p) == h
```

## The flag

```
flag{...} | CTF{...} — after decrypt/forge, not in the scalar
```

## The record

```
post-probe (evidence ⊆ response) → field-notes →
classify_solve (solve) / attempts (fail) → decide.py (stuck)
```

## The honest status

Catalogue — no local solve; corpus is the field procedure.
