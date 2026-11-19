# Detection map — the signal → the class → the file

## The count signals

- `moduli ≥ 2` → `batch-gcd`/`hastad` → `batch-gcd.md`, `hastad.md`
- `moduli = 1` → single-modulus → `detection.md`, `fermat.md`, `wiener.md`, …
- `e count = 2` on one `n` → `common-modulus` → `common-modulus.md`
- `c count ≥ e`, same `m` → `hastad` → `hastad.md`

## The exponent signals

- `e` = 3/5/17 → `small-e-root`/`hastad`/`franklin-reiter` → `small-e-root.md`
- `e` = 65537 → the default → `detection.md`
- `e` ~ `n` → `wiener`/`boneh-durfee` → `wiener.md`, `boneh-durfee.md`
- `gcd(e,phi)>1` → `eth-root` → `factor-from-d.md`

## The keygen signals

- `next_prime`/`p+k`/`q=p+2` → `fermat` → `fermat.md`
- `getPrime(small)` for `d` → `wiener`/`boneh-durfee`
- `random.seed`/`reused p` → `batch-gcd`
- `p-1` smooth → `pollard-pm1`
- `e=3`, no pad → `small-e-root`/`hastad`
- `m2=a·m1+b` → `franklin-reiter`

## The leak signals

- `d`/`phi`/`dp` → `factor-from-d`/`crt` → `factor-from-d.md`, `crt.md`
- `p`-high/low → `coppersmith-*` → `coppersmith.md`
- partial `m` → `coppersmith` partial-message → `coppersmith.md`
- correct+faulty sig → `crt` Bellcore → `crt.md`

## The format signals

- `.pem`/`.der` → `n`,`e` only → `detection.md`
- `.json` list → batch → `batch-gcd.md`
- `priv.pem` fields → `crt`/`factor-from-d`
- `.txt` numbers → the sheet → `parameter-sheet.md`
- `.py` source → the comment → `recon-order.md`
