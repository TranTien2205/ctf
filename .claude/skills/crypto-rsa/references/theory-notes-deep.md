# Theory notes deep — the working facts, expanded

## The RSA identity

`n = p·q`, `φ=(p-1)(q-1)`, `ed ≡ 1 mod φ`. `c = m^e mod n`, `m = c^d mod n`.
`pow(m,e,n)==c` is the verify — the definition of decryption.

## The six violation families, restated

1. **Wrap** — `m^e<n` → `c` is a plain power → `integer_nthroot`. `e` small +
   `m` short. Across `e` coprime `n` → CRT + root (`hastad`).
2. **Gap** — `|p-q|` small → `n=a²-b²`, `a` near `√n` → `fermat`.
3. **Divisor** — shared `p` (`gcd`) or `p-1` smooth (`a^{B!}≡1 mod p`) →
   `batch-gcd`, `pollard-pm1`.
4. **Exponent** — `ed≡1 mod φ` leaks `d`: `d<n^0.25` (Wiener CF),
   `d<n^0.292` (Boneh-Durfee), `gcd(e1,e2)=1` (Bezout), `d`/`phi`/`dp` held.
5. **Partial** — bits of `p`/`m` → Coppersmith small-root; the window `n^0.25`
   (factor) or `n^(1/e)` (message).
6. **Relation/leak** — `m2=a·m1+b` (Franklin-Reiter `gcd`), a fault (Bellcore
   `gcd`), `d`/`phi`/`dp`/`p`,`q` (arithmetic), `gcd(e,phi)>1` (`eth-root`).

## The bounds, ordered

```
d < n^0.25      wiener          (CF, deterministic)
d < n^0.292     boneh-durfee    (lattice ceiling)
window ≥ n^0.25 coppersmith-β½  (factor recovery)
window ≥ n^(1/e) coppersmith-msg (message recovery)
m^e < n         small-e/nth-root (exact)
≥e n's          hastad          (CRT + root)
gcd(e1,e2)=1    common-modulus  (Bezout)
|p-q| small     fermat          (a-climb O(|p-q|))
B ≥ p-1 factor  pollard-pm1     (gcd(a^{B!}-1,n))
∏pi > m         crt             (residues)
linear          franklin-reiter (poly gcd)
gcd(e,phi)>1    eth-root        (the g candidates)
```

## The non-obvious facts

- A large `e` *is* the small-`d` tell — `e=inverse(d,phi)` for small `d` ≈ `n`.
- `e=3` is weak only when `m³<n` — a real flag usually wraps.
- `n` count is not the bug — a *collision* (`gcd>1`) is.
- Balanced primes ≠ close — `fermat` needs `|p-q|` small in *value*.
- A public PEM is `n`,`e` only.
- `inverse(e,phi)` failing → `gcd(e,phi)>1` → `eth-root`, not a bug.
- `n=p²` → `phi=p(p-1)`; `n` prime → `phi=n-1`.
- `pow(m,e,n)==c` is the gate — a flag-shaped string that fails is a decoy.

## The verify

`pow(m,e,n)==c` or `p*q==n`. Both deterministic — run them.
