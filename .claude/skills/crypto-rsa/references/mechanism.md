# Mechanism — the six RSA violation primitives

RSA = `n=p·q`, `ed≡1 mod φ`, `c=m^e mod n`. Secure iff `p`,`q` unrecoverable.
Every attack violates one of six preconditions:

1. **wrap** — `m^e<n` → exact root → `small-e-root`,`nth-root`,`hastad`.
2. **gap** — `|p-q|` small → `n=a²-b²` → `fermat`.
3. **divisor** — shared `p` / smooth `p-1` → `gcd` → `batch-gcd`,`pollard-pm1`.
4. **exponent** — `d` small or `e` shared → `wiener`,`boneh-durfee`,
   `common-modulus`,`factor-from-d`.
5. **partial** — `p`/`m` bits known → `coppersmith-*`.
6. **relation/leak** — `m2=a·m1+b`,a fault,`d`/`phi`/`dp`/`p`,`q` →
   `franklin-reiter`,`crt`,`factor-from-d`,`rsa-decrypt`,`eth-root`.

The bound is the falsifier. The verify is `pow(m,e,n)==c` / `p*q==n`. See
`mechanism-deep.md`, `mechanism-map.md`, `mechanism-catalogue.md`.
