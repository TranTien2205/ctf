# Quick reference deep — the two-screen card

## The group read

```
p   field prime
a b curve coeffs            y² = x³ + ax + b
G   generator               ord(G) = n
n   subgroup order          --order is ALWAYS n
Q   public point = d·G      the verify target
sigs [{"r","s","z"}]        --sigs FILE, z = int(H(m)) truncated
```

## The attack table

```
SHAPE                          COMMAND
r dup                        ecdsa-nonce-reuse --sigs f --order n
k < B                        hnp-ecdsa --sigs f --order n --nonce-bits B
(t,u)                        hnp --t f --u f --modulus n --bound B
ord smooth                   pohlig-hellman --g g --h h --p p --order n
x bounded                    bsgs --g --h --p --order B
ord ?                        smoothness --n n
#E == p                      tools/crypto/smart_attack.py
Δ == 0                       tools/crypto/singular_ec.py
unvalidated P                tools/crypto/ec.py + bsgs/pohlig + CRT
```

## The count

```
hnp.required_signatures(order_bits, nonce_bits) ≈ 2·order_bits/leaked
```

## The bounds

```
bsgs ord ≤ 2^44      PH largest factor ≤ 2^40
Δ exact 0            #E exact p       B covers all k
```

## The verify

```
E.mul(G, d) == Q     pow(g, x, p) == h
```

## The record

```
post-probe (evidence ⊆ response) → field-notes → classify_solve/attempts
```
