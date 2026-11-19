# Parameter sheet deep — the fields, annotated

## The counts

- **`n` count** — the moduli: 1 → single-modulus; ≥2 → `batch-gcd`/`hastad`.
- **`e` count** — on 1 `n`: 2 → `common-modulus`; 1 → single-key.
- **`c` count** — the ciphertexts: ≥`e` same `m` → `hastad`; 2 → `common-modulus`/`franklin-reiter`.

## The sizes

- **`n` bits** — 512/1024/2048/4096 — context; small `n` may be factorable.
- **`e` bits** — `e`≈`n` → small `d`; `e`=3/5/17/257 → small-`e` family.
- **`m` bits** — `m^e<n` → the wrap.

## The exponent signature

- `e_sig` = `small` (3/5/17/257) | `medium` (65537) | `large` (`e`≈`n`) |
  `gcd>1` (`gcd(e,phi)>1`) | `one` (`e`=1).

## The leak

- `p`/`q` — `factor-from-d`/`rsa-decrypt`/`eth-root`.
- `d`/`phi` — `factor-from-d`/`rsa-decrypt`.
- `dp`,`dq`,`qInv` — `crt` manual.
- `p`/`m` bits — `coppersmith-*`.
- `sig` + `sig_faulty` — `crt` Bellcore.
- `m` residues `mod pi` — `crt`.

## The keygen tell

`next_prime`/`p+k`/`q=p+2` → `fermat` · `seed`/reused `p` → `batch-gcd` ·
`getPrime(d)` small → `wiener`/`boneh-durfee` · `p-1` smooth → `pollard-pm1` ·
`e=3`,no pad → `small-e`/`hastad` · `m2=a·m1+b` → `franklin-reiter` ·
`dp`,`dq`,`qInv` → `crt` · `d`/`phi`/`p`,`q` printed → `factor-from-d`/`rsa-decrypt`
· `redact`/`XXXX`/`mask` → `coppersmith`/`crt`/`factor-from-d` ·
`for n in ns` broadcast → `hastad` · `e1`,`e2` on `n` → `common-modulus`.

## The degenerate

`n`=p² → `phi=p(p-1)` · `n` prime → `phi=n-1` · `n` smooth → `factorint` ·
`n` multi-prime → `phi=∏(pi-1)` · `n` small → a table.
