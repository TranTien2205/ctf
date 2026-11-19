# Theory deep — the working facts

## The identity

`n=p·q`, `φ=(p-1)(q-1)`, `ed≡1 mod φ`, `c=m^e mod n`, `m=c^d mod n`.
`pow(m,e,n)==c` is the verify.

## The six families

1. **Wrap** — `m^e<n` → `c` a plain power → `integer_nthroot`/`hastad`.
2. **Gap** — `|p-q|` small → `n=a²-b²` → `fermat`.
3. **Divisor** — shared `p` (`gcd`)/`p-1` smooth (`a^{B!}`) → `batch-gcd`/`pollard-pm1`.
4. **Exponent** — `ed≡1` leaks `d` — `n^0.25` (Wiener CF), `n^0.292`
   (Boneh-Durfee), `gcd=1` (Bezout), `d`/`phi`/`dp` held.
5. **Partial** — bits → Coppersmith; `n^0.25`/`n^(1/e)`.
6. **Relation/leak** — `a·m1+b` (Franklin-Reiter `gcd`), `sig` fault (Bellcore),
   `d`/`phi`/`dp`/`p`,`q`, `gcd(e,phi)>1` (`eth-root`).

## The bounds

`d<n^0.25` wiener · `d<n^0.292` boneh-durfee · window `n^0.25`/`n^(1/e)`
coppersmith · `m^e<n` small-e · `≥e` n's hastad · `gcd=1` common-modulus ·
`|p-q|` fermat · `B`≥factor pollard-pm1 · `∏pi>m` crt · linear franklin-reiter ·
`gcd(e,phi)>1` eth-root · the value held factor-from-d/rsa-decrypt.

## The facts

- Large `e` = small `d` tell.
- `e=3` weak only when `m³<n`.
- `n` count ≠ the bug — a collision is.
- Balanced ≠ close — `fermat` needs small `|p-q|`.
- `inverse(e,phi)` fails → `gcd(e,phi)>1` → `eth-root`.
- `n=p²` → `phi=p(p-1)`; `n` prime → `phi=n-1`.
- `pow(m,e,n)==c` is the gate.
