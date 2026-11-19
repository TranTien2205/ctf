# Operator checklist — the field run, ordered

## 0. Setup

- [ ] `selfcheck.py` green.
- [ ] `tools/crypto/{ec,dlog,hnp,smart_attack,singular_ec,lll,numtheory}.py --selftest` each pass.

## 1. Inventory

- [ ] Params extracted: `p a b G Q n` or curve name.
- [ ] Sigs counted, `r` deduped.
- [ ] `z` convention chosen.
- [ ] Oracle probed (deterministic? validates?).

## 2. Gates

- [ ] `r` dup? → `ecdsa-nonce-reuse`.
- [ ] `smoothness --n` → `pohlig-hellman` vs `bsgs`.
- [ ] `Δ == 0`? → `singular_ec`.
- [ ] `#E == p`? → `smart_attack`.
- [ ] `k` bound? → `hnp-ecdsa`/`hnp`.
- [ ] validation? → invalid curve.

## 3. Solve

- [ ] Correct attack id, correct flags (`payload-dictionary*`).
- [ ] `--sigs` JSON file (not inline).
- [ ] `--order` = `n`.
- [ ] `required_signatures` met.

## 4. Verify

- [ ] `x·G == Q` or `pow(g, x, p) == h` against supplied params.
- [ ] `flag{`/`CTF{` in the decoded output.

## 5. Close

- [ ] `post-probe` recorded with verbatim output.
- [ ] Fail → `knowledge/attempts/` falsifier.
- [ ] Solve → `classify_solve.py`.
- [ ] Stuck → `decide.py` rungs.
