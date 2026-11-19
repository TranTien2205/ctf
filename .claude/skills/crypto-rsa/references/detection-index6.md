# Detection index6 — the read-order index

## Phase 0 — the passive reads

- `ls`/`file`/`xxd` — the types → `.pem`/`.der`/`.json`/`.txt`/`.py`/`.bin`/`.pcap`.
- `RSA.importKey` — `n`,`e`,`d`/`p`/`q`/`dp`/`dq`/`qInv`.
- `re.findall` — the `n`,`e`,`c` integers + counts.
- `keygen`/`chal` grep — the tell.
- `crypto_attack.py list` — the ids + `lll_backend`.

## Phase 1 — the arithmetic reads

- `n`,`e`,`c` counts — `detection-matrix*`.
- `e` size — `e≈n` → `wiener`/`boneh-durfee`.
- `gcd(e,phi)` — `>1` → `eth-root`.
- `n` square/prime/smooth — degenerate.
- `m^e` vs `n` — `m^e<n` → `small-e`.

## Phase 2 — the discriminating reads

- `gcd(ni,nj)` — `batch-gcd`.
- `gcdex(e1,e2)` — `common-modulus`.
- `a²-n` square — `fermat`.
- CF `k/d` — `wiener`.
- `gcd(a^{B!}-1,n)` — `pollard-pm1`.
- `crt`/`integer_nthroot` — `hastad`/`small-e`/`crt`.

## Phase 3 — the verify

- `pow(m,e,n)==c` — the plaintext gate.
- `p*q==n` — the factor gate.
