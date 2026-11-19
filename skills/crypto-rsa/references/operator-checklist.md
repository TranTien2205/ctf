# Operator checklist — the run, step by step

## Phase 0 — inventory

- [ ] `python3 selfcheck.py` green.
- [ ] `crypto_attack.py list` — the ids + `lll_backend` noted.
- [ ] Every artifact read — `.pem`/`.der`/`.json`/`.txt`/`.py`/`.bin`/`.pcap`.
- [ ] `RSA.importKey` on every key — `n`,`e`,private fields recorded.
- [ ] The integers counted — `n`,`e`,`c` counts.
- [ ] `keygen`/`chal`/`gen` grep'd — the tell found.

## Phase 1 — the sheet

- [ ] `n` count — ≥2 → `batch-gcd`/`hastad`; 1 → single-modulus.
- [ ] `e` count — 2 on 1 `n` → `common-modulus`.
- [ ] `c` count — ≥`e` → `hastad`.
- [ ] `e_sig` — small/medium/large/`gcd>1`.
- [ ] `leak` — `p`/`m` bits, `d`/`phi`/`dp`/`qInv`/`p`,`q`, `sig`+fault, `m` residues.
- [ ] `keygen` — the tell.
- [ ] `degenerate` — `n`=p²/prime/smooth/multi.
- [ ] `m^e` vs `n` — the wrap.

## Phase 2 — the attack

- [ ] `attack-table.md` — the first-yes row picked.
- [ ] `per-bound.md` — the falsifier read.
- [ ] `crypto_attack.py <id> --help` — the flags confirmed.
- [ ] The attack run — the output captured.
- [ ] The chain run — `factor-from-d`/`rsa-decrypt`/`factor`/`d`/`phi`/`m`.

## Phase 3 — the verify

- [ ] `pow(m,e,n)==c` or `p*q==n` or `pow(c,d,n)==m` — run, not assumed.
- [ ] `long_to_bytes(m)` — the pad stripped, the flag bytes present.
- [ ] A `m` that fails `pow` — a decoy/wrong root, not a flag.

## Phase 4 — the record

- [ ] `post-probe --verdict confirms --evidence-kind impact --evidence --response`.
- [ ] `classify_solve.py --chain <id>` after a solve.
- [ ] `knowledge/attempts/<challenge>.json` for a dead end.
- [ ] `../field-notes.md` (skill root) updated.
- [ ] `decide.py` for the budget/escalation.
