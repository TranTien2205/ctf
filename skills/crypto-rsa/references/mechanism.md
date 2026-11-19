# Mechanism — the six violation families

RSA is `n=p·q`, `φ=(p-1)(q-1)`, `ed≡1 mod φ`. A violation weakens `n`/`d`/`φ`/`m`
in one of six ways.

## Wrap — `m^e<n`

`c=m^e mod n`; `m^e<n` → `c=m^e` — a plain integer power, no wrap. Across `e`
coprime `n` → `m^e<∏ni` → CRT a plain power. `small-e-root`/`nth-root`/`hastad`.

## Gap — `|p-q|` small

`n=p·q`, `|p-q|` small → `n=a²-b²`, `a=(p+q)/2` near `√n` → `fermat` walks `a`.

## Divisor — a shared/smooth factor

`gcd(ni,nj)=p` (shared `p`) → `batch-gcd`; `gcd(a^{B!}-1,n)=p` (`p-1` `B`-smooth)
→ `pollard-pm1`.

## Exponent — `ed≡1 mod φ` leaks `d`

`d<n^0.25` → CF → `wiener`; `d<n^0.292` → LLL → `boneh-durfee`; `gcd(e1,e2)=1`
→ Bezout → `common-modulus`; `d`/`phi`/`dp`/`qInv`/`p`,`q` held → `factor-from-d`/
`crt`/`rsa-decrypt`.

## Partial — bits → Coppersmith

`p`/`m` = known + small unknown → `f(x)≡0 mod p`/`mod n` small root →
`coppersmith-*`.

## Relation/leak — structure

`m2=a·m1+b` → `franklin-reiter`; `sig` fault/`dp`/`m` residues → `crt`;
`gcd(e,phi)>1` → `eth-root`; `p`,`q`/`d`/`phi` → `rsa-decrypt`/`factor-from-d`.

## The verify

`pow(m,e,n)==c` / `p*q==n` — the mechanism-neutral gate.
