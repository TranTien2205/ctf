# Detection checklist deep — the full audit before attacking

## The artifact

- [ ] Every file listed — `.pem`/`.der`/`.crt`/`.key`/`.json`/`.txt`/`.py`/`.bin`/`.pcap`.
- [ ] `keygen.py`/`chal.py`/`gen.py` read — the misuse line found (`next_prime`,
      `seed`, `getPrime(d)`, `p-1`, `e=3`, no pad, `m2=a·m1+b`, `dp`,`dq`,`qInv`,
      `d`/`phi` printed, `redact`/`XXXX`).
- [ ] `RSA.importKey` on every key/cert — `n`,`e`,private fields (`d`,`p`,`q`,
      `dp`,`dq`,`qInv`) recorded.
- [ ] The integers parsed — `re.findall(r'(?:0x)?[0-9a-fA-F]{20,}|\b\d{20,}\b')`.
- [ ] A `.pcap` → `tshark`/`scapy` for the handshake `n`,`e` and the `c`.

## The counts

- [ ] `n` count — ≥2 → `batch-gcd`/`hastad`; 1 → single-modulus.
- [ ] `e` count on 1 `n` — 2 → `common-modulus`.
- [ ] `c` count — ≥`e` same `m` → `hastad`.

## The exponent

- [ ] `e` small (3/5/17/257) → `small-e`/`hastad`/`franklin-reiter`.
- [ ] `e`=65537 → the bug is elsewhere (a leak, the primes, a relation).
- [ ] `e`~`n` → `wiener`/`boneh-durfee`.
- [ ] `gcd(e,phi)>1` (if `phi`/`p`,`q` known) → `eth-root`.
- [ ] `e`=1 → `m=c` trivially.

## The leak

- [ ] `d`/`phi`/`dp`/`dq`/`qInv`/`p`/`q` present → `factor-from-d`/`crt`/
      `rsa-decrypt`/`eth-root`.
- [ ] `p`-high/low bits → `coppersmith-high-bits`/`-core`.
- [ ] `m` partial → `coppersmith` partial-message.
- [ ] a correct+faulty `sig` pair → `crt` Bellcore.

## The degenerate

- [ ] `isqrt(n)**2==n` → `n=p²` → `phi=p(p-1)`.
- [ ] `isPrime(n)` → `phi=n-1`.
- [ ] `factorint(n)` → a smooth `n` → direct.
- [ ] `n` multi-prime → `phi=∏(pi-1)`.

## The route

- [ ] `crypto_attack.py list` — the inventory + bounds.
- [ ] `attack-table.md` — the first-yes row picked.
- [ ] `per-bound.md` — the falsifier read before the run.
- [ ] `lll_backend` noted — `fpylll` absent → pure-python LLL.
