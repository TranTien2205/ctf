# pollard-pm1 — the smooth-predecessor split

`p-1` `B`-smooth → `a^{B!}≡1 mod p` → `gcd(a^{B!}-1,n)=p`. Detection: a weak
`p`/`p-1` smooth hint in keygen. Bound: `B`≥largest `p-1` factor; `gcd=1` at `B`
→ raise `B` or closed. Verify: `1<gcd<n`, `p*q==n`. Command: `crypto_attack.py
pollard-pm1 --n --b`. See `per-attack-pollard-pm1.md`.
