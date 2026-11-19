# common-modulus — the shared-modulus Bezout attack

`c1=m^e1`,`c2=m^e2` mod `n`, `gcd(e1,e2)=1` → `m=c1^a·c2^b`. Detection: 1 `n`, 2
`e`, same `m`. Bound: `gcd(e1,e2)=1` — `gcd>1` → `m^gcd`, then `nth-root` if
`m^gcd<n`. Verify: `pow(m,e1,n)==c1`. Command: `crypto_attack.py common-modulus
--n --e1 --c1 --e2 --c2`. See `per-attack-common-modulus.md`.
