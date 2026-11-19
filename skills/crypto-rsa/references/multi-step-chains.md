# Multi-step chains — the attacks that compose

## Factor → decrypt

```
fermat / batch-gcd / pollard-pm1 / coppersmith / crt-Bellcore / factor-from-d
   → p, q
   → phi = (p-1)(q-1)
   → d = inverse(e, phi)
   → m = c^d mod n
   → pow(m,e,n)==c
```

The most common chain: an attack recovers a factor, `rsa-decrypt` turns it into
the plaintext.

## d → decrypt

```
wiener / boneh-durfee / factor-from-d / crt-dp
   → d (or p → d)
   → m = c^d mod n
   → pow(m,e,n)==c
```

## Root → flag

```
small-e-root / nth-root / hastad / common-modulus / franklin-reiter / eth-root
   → m
   → pow(m,e,n)==c
   → long_to_bytes(m) → strip pad → flag
```

## The dp chain

```
handout leaks dp (d mod p-1)
   → for k in 1..e: if (e*dp-1)%k==0: p=(e*dp-1)/k+1; if n%p==0 → p
   → factor-from-d → rsa-decrypt → m
```
`crypto_attack.py crt` or `factor-from-d` handles the loop.

## The Bellcore chain

```
correct sig s + faulty sig s' of the same m
   → gcd(s'^e - m, n) = q
   → p = n/q
   → factor-from-d → rsa-decrypt
```
`# Bellcore is manual: gcd(pow(s_f,e,n)-m, n) — not a crypto_attack.py id

## The coppersmith chain

```
leaked high bits a of p
   → coppersmith-high-bits → x (the unknown low)
   → p = a + x
   → factor-from-d → rsa-decrypt
```

## The eth-root chain

```
gcd(e, phi) > 1
   → p, q held → the gcd candidates
   → for each m_i: pow(m_i, e, n) == c + flag format → the true root
```

## The broadcast chain

```
same m to e recipients
   → hastad: CRT → m^e mod ∏ni → integer_nthroot → m
   → pow(m,e) == the CRT value
```

## The rule

A chain is only as strong as its last `pow` verify — run it on every step.
