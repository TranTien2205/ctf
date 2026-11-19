# per-attack common-modulus deep — the shared-modulus Bezout, the full treatment

## The mechanism

`c1 = m^e1 mod n`, `c2 = m^e2 mod n`, `gcd(e1,e2)=1`. Bezout gives `a·e1+b·e2=1`
→ `m^{a·e1+b·e2} = m` → `m = c1^a·c2^b mod n`.

## Detection

- one `n`, two `e`, two `c` of the same `m`.
- a shared-modulus broadcast; "we reuse n".

## The bound / falsifier

`gcd(e1,e2)=1`. `gcd>1` → `m^gcd`, not `m` — then `nth-root` if `m^gcd<n`.

## The attack

```bash
crypto_attack.py common-modulus --n <n> --e1 <e1> --c1 <c1> --e2 <e2> --c2 <c2>
```

```python
g,a,b = gcdex(e1,e2); assert g==1
m = pow(c1,a,n)*pow(c2,b,n) % n; assert pow(m,e1,n)==c1
```

## The verify

`pow(m,e1,n)==c1` — `m` re-encrypts.

## Variants

- `gcd>1` → `m^gcd`; `small-e`/`nth-root` on it.
- >2 exponents — pairwise Bezout.
- A private `d` for one `e` → `rsa-decrypt` directly.

## Failure modes

- `gcd>1` — `m^gcd`.
- different `m` per `c` — not shared-`m`.

## The honest status

Standard — catalogue.
