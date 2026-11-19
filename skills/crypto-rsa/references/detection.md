# Detection — fingerprinting the RSA weakness

Read `recon-order.md`: source → count → exponent → leak → relation → degenerate.

- **source**: `keygen.py` — `next_prime`/`seed`/`getPrime(d)`/`p-1`/`e=3`/no pad.
- **counts**: `n`≥2 → batch/hastad; `e` count 2 → common-modulus; `c`≥`e` → hastad.
- **exponent**: `e` small / 65537 / ~`n` / `gcd(e,phi)>1`.
- **leak**: `d`,`phi`,`dp`,`p`-bits,`m`-partial,`p`,`q`.
- **relation**: `m2=a·m1+b`, residues, a fault.
- **degenerate**: `n` square / prime / multi-prime.

The fingerprint → `attack-table.md` row → the attack. See `detection-deep.md`,
`detection-checklist.md`, `detection-matrix.md`, `detection-catalogue.md`,
`detection-variants.md`, `detection-surface.md`, `detection-index.md`,
`detection-map.md`, `detection-playbook.md`.
