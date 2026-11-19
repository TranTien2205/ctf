# Detection checklist — run every line before attacking

## The artifact

- [ ] Files listed — `.pem`/`.der`/`.crt`/`.json`/`.txt`/`.py`/`.bin`.
- [ ] `keygen.py`/`chal.py` read — the misuse line found.
- [ ] `RSA.importKey` on every key/cert — `n`,`e`,private fields recorded.
- [ ] The integers parsed — `re.findall(r'\d{20,}')`.

## The counts

- [ ] `n` count — ≥2 → `batch-gcd`/`hastad`; 1 → single-modulus.
- [ ] `e` count on 1 `n` — 2 → `common-modulus`.
- [ ] `c` count — ≥`e` same `m` → `hastad`.

## The exponent

- [ ] `e` small (3/5/17/257) → `small-e`/`hastad`/`franklin-reiter`.
- [ ] `e`=65537 → the bug is elsewhere.
- [ ] `e`~`n` → `wiener`/`boneh-durfee`.
- [ ] `gcd(e,phi)>1` (if `phi`/`p`,`q` known) → `eth-root`.

## The keygen

- [ ] `next_prime`/`p+k`/`q=p+2` → `fermat`.
- [ ] `getPrime(d)` small → `wiener`/`boneh-durfee`.
- [ ] `random.seed` → `batch-gcd`.
- [ ] `p-1` smooth → `pollard-pm1`.
- [ ] `e=3`,no pad → `small-e`/`hastad`.
- [ ] `m2=a·m1+b` → `franklin-reiter`.
- [ ] `dp`,`dq`,`qInv` → `crt`.
- [ ] `d`/`phi` printed → `factor-from-d`.
- [ ] `redact`/`XXXX` → `coppersmith`/`crt`/`factor-from-d`.

## The degenerate

- [ ] `isqrt(n)**2==n` → `n=p²`.
- [ ] `isPrime(n)` → `n` prime.
- [ ] `factorint(n)` → smooth `n`.

## The route

- [ ] `crypto_attack.py list` — the inventory + bounds.
- [ ] `attack-table.md` — the first-yes row.
- [ ] `per-bound.md` — the falsifier.
