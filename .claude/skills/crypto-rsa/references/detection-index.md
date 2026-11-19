# Detection index — every signal, its file, its attack

## By the object you read first

### The source comment
- `next_prime(p)` / `q=p+2` / `p+k` → `fermat` — `fermat.md`
- `getPrime(256)` for `d` / `d small` → `wiener` / `boneh-durfee`
- `random.seed` / `reused p` / `leaked seed` → `batch-gcd` / a shared prime
- `p = getPrime(512)` then `smooth(p-1)` → `pollard-pm1`
- `e = 3`, `pad=None` / `m` short → `small-e-root` / `hastad`
- `encrypt(m1)` and `encrypt(a*m1+b)` → `franklin-reiter`
- `dp`,`dq`,`qInv` in the handout → `crt`
- `d` or `phi` printed → `factor-from-d` / `rsa-decrypt`
- `redact` / `XXXX` on `p` → `coppersmith-high-bits` / `coppersmith-core`

### The file type
- `.pem` / `.der` / `.key` / `.crt` public → `n`,`e` only → the sheet
- `.pem` / `.der` private with fields present → `crt` / `factor-from-d`
- `.json` / `.txt` of moduli → `batch-gcd`
- `.py` / `.txt` of `n`,`e`,`c` → the sheet
- a `.pcap` / socket → a service — transport or oracle

### The numbers
- `e` = 3/5/17/257 → small-e → `small-e-root`, `hastad`, `franklin-reiter`
- `e` = 65537 → default — the bug is elsewhere
- `e` ~ `n` (same bit-length) → `wiener` / `boneh-durfee`
- `e` coprime to `φ` fails (`gcd>1`) → `eth-root`
- `n` a perfect square / prime → degenerate `phi`
- `c` ~ `n` → `m` wrapped — not a root attack

### The counts
- `n` count ≥ 2 → `batch-gcd` or `hastad`
- `e` count = 2, same `n` → `common-modulus`
- `c` count ≥ `e`, same `m` → `hastad`
- `p`,`q`,`dp`,`dq`,`qInv` present → `crt` / `factor-from-d`
- a single `n`,`e`,`c` and nothing else → the single-modulus attacks

## The files

`detection.md`, `detection-deep.md`, `detection-checklist.md`,
`detection-matrix.md`, `detection-playbook.md`, `detection-variants.md`,
`detection-surface.md`, `detection-catalogue.md`, `parameter-sheet.md`,
`recon-order.md`, `probe-catalogue.md`, `probe-map.md`, `lead-grammar.md`
