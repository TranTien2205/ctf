# Multi-step chains deep — the composite recoveries

## The factor → decrypt chain

`p`/`q` (a factor recovery) → `phi=(p-1)(q-1)` → `d=pow(e,-1,phi)` →
`m=pow(c,d,n)` → `pow(m,e,n)==c` → `long_to_bytes(m)` → the flag.

```
fermat/batch-gcd/pollard-pm1/coppersmith → p,q → rsa-decrypt --p --q → m
```

## The d → decrypt chain

`d` (wiener/boneh-durfee/factor-from-d/dp) → `m=pow(c,d,n)` → `pow` → flag.

```
wiener/boneh-durfee → d → pow(c,d,n) → m
factor-from-d → p,q → rsa-decrypt → m
crt dp → p → factor-from-d → p,q → rsa-decrypt → m
```

## The phi → decrypt chain

`phi` (held/factor-from-d) → `d=pow(e,-1,phi)` → `m` → `pow`.

## The direct-m chain

`m` (small-e/nth-root/hastad/common-modulus/franklin-reiter/crt/eth-root) →
`pow(m,e,n)==c` → `long_to_bytes` → strip a pad → the flag.

## The pad chain

`m` → `pow(m,e,n)==c` on the *padded* block → `long_to_bytes` → unpad
`\x00\x02<pad>\x00`/OAEP → the flag.

## The eth-root chain

`p`,`q` → the `g` candidates (CRT of `g_p`×`g_q` roots) → `pow(m_i,e,n)==c` +
flag format → the true `m`.

## The escalated chain

`wiener` no-find → `boneh-durfee` → `boneh-durfee-escalate` → `p`,`q`/`d` →
`rsa-decrypt` → `m`.

## The verify chain

Every step asserts — `p*q==n`, `pow(m,e,n)==c`, `pow(c,d,n)==m`,
`1<p<n`&`p|n`, `n-phi+1==p+q`.
