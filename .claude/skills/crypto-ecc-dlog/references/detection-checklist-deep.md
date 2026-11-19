# Detection checklist deep — the run-list with failure branches

## Inventory run-list

- [ ] `p a b G Q n` (or curve name) extracted → if missing `n`, count `#E`
      or read the challenge intent (defect vs generic).
- [ ] Sigs counted → `<2` ends nonce path; `≥ required_signatures` enables HNP.
- [ ] `r` deduped → pair → `ecdsa-nonce-reuse`.
- [ ] `z` convention chosen → FIPS truncation; `mod n` fallback on verify fail.
- [ ] Oracle probed → deterministic/validation recorded.

## Gate run-list

- [ ] `smoothness --n ord` → largest factor decides PH.
- [ ] `Δ = -16(4a³+27b²) mod p` → `0` → `singular_ec`.
- [ ] `#E == p` → `smart_attack`.
- [ ] `pow(h, ord, p) == 1` → `h ∈ <g>`.
- [ ] `--order` is `n` (subgroup), not `p`.

## Solve run-list

- [ ] Correct attack id from `detection-matrix.md`.
- [ ] `--sigs` JSON file — `[r,s,z]`/`{"r","s","z"}` — never inline.
- [ ] `--nonce-bits B` = `k < 2^B`; `--nonce-bound B` = `k < B`.
- [ ] `--t`/`--u` aligned integer lists for `hnp`.

## Verify run-list

- [ ] `x·G == Q`/`pow(g,x,p) == h` against the supplied params.
- [ ] `flag{`/`CTF{` present after the flag step (decrypt/forge).

## Record run-list

- [ ] `post-probe` evidence ⊆ response.
- [ ] `../field-notes.md` entry.
- [ ] Fail → `knowledge/attempts/` falsifier.
- [ ] Solve → `classify_solve.py` card.
- [ ] Stuck → `decide.py` rung recorded.
