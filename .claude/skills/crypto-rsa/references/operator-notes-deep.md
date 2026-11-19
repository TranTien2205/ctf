# Operator notes deep — the field-guide details

## The order

`list` → `parameter-sheet` → `attack-table` → `per-bound` → `crypto_attack.py`
→ `verify` → `field-notes`. Never open a depth file before the sheet.

## The sheet, one more time

- `n` count — ≥2 → `batch-gcd`/`hastad`; 1 → single-modulus.
- `e` count on 1 `n` — 2 → `common-modulus`.
- `c` count — ≥`e` same `m` → `hastad`.
- `e_sig` — small/medium/large-`n`/`gcd>1`.
- `leak` — `p`/`m` bits, `d`/`phi`/`dp`/`qInv`/`p`,`q`, `sig`+faulty, `m` residues.
- `keygen` — `next_prime`,`seed`,`getPrime(d)`,`p-1`,`e=3`,no pad,`a·m1+b`,
  `dp`,`dq`,`qInv`,`redact`.
- `degenerate` — `n`=p²/prime/smooth/multi.
- `m^e` vs `n` — the wrap check.

## The tools

- `crypto_attack.py list` — the inventory + bounds; `lll_backend` for `fpylll`.
- `crypto_attack.py <id> --help` — the flags. `<id> --json`, `--in <file>`.
- `tools/crypto/franklin_reiter.py` — `franklin-reiter`, manual.
- `tools/crypto/` — LLL (`tools/crypto/lll.py`), CRT (`tools/crypto/numtheory.py`).
- `sympy` — `gcdex`,`factorint`,`crt`,`integer_nthroot`,`isprime`.
- `Crypto` — `RSA`,`long_to_bytes`,`bytes_to_long`,`inverse`.

## The verify

`pow(m,e,n)==c` / `p*q==n` — run them.

## The record

`post-probe --hypothesis-id --class --verdict --evidence-kind --evidence
--response` · `classify_solve.py --chain <id>` · `knowledge/attempts/` for a
dead end · `../field-notes.md` (skill root).
