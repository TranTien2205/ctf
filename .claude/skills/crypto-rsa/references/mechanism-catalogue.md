# Mechanism catalogue — the six primitives, the bound, the verify

## Wrap — `m^e<n`

- The identity: `c=m^e mod n`; `m^e<n` → `c=m^e` — a plain integer power.
- The bound: `m^e<n` (single) / `m^e<∏ni` (broadcast).
- The attacks: `small-e-root`/`nth-root` (`c^{1/e}`), `hastad` (CRT+root).
- The verify: `pow(m,e)==c` — plain, no `mod n`.

## Gap — `|p-q|` small

- `n=p·q`, `|p-q|` small → `n=a²-b²`, `a=(p+q)/2` near `√n`.
- The bound: the `a` walk `O(|p-q|)` — small gap.
- The attack: `fermat`.
- The verify: `p*q==n`.

## Divisor — a shared/smooth factor

- `gcd(ni,nj)=p` (shared) → `batch-gcd`; `gcd(a^{B!}-1,n)=p` (`p-1` `B`-smooth)
  → `pollard-pm1`.
- The bound: a `gcd>1` / `p-1` `B`-smooth.
- The verify: `1<p<n`, `p|n`, `p*q==n`.

## Exponent — `ed≡1 mod φ` leaks `d`

- `d<n^0.25` → CF → `wiener`; `d<n^0.292` → LLL → `boneh-durfee`;
  `gcd(e1,e2)=1` → Bezout → `common-modulus`; `d`/`phi`/`dp`/`qInv`/`p`,`q`
  held → `factor-from-d`/`crt`/`rsa-decrypt`.
- The bound: the `n^α`/`gcd`/held-value forms.
- The verify: `pow(c,d,n)==m`/`pow(m,e,n)==c`.

## Partial — bits → Coppersmith

- `p`/`m` = known + small unknown → `f(x)≡0 mod p`/`mod n` small root →
  `coppersmith-*`.
- The bound: window `n^0.25` (factor) / `n^(1/e)` (message).
- The verify: `p|n` / `pow(m,e,n)==c`.

## Relation/leak — structure

- `m2=a·m1+b` → `franklin-reiter`; `sig` fault / `m` residues / `dp` → `crt`;
  `gcd(e,phi)>1` → `eth-root`; `p`,`q`/`d`/`phi` → `rsa-decrypt`/`factor-from-d`.
- The bound: the relation/leak present.
- The verify: `pow`/`gcd`/`p*q`.
