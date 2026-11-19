# Checklist deep — the full run-sheet

## Phase A — inventory

- [ ] `p`, `a`, `b`, `G`, `Q`, `n` (or curve name) extracted.
- [ ] Signatures counted, `r` list deduped.
- [ ] `z` convention chosen (FIPS truncation first).
- [ ] Oracle shape probed (deterministic? validates points?).
- [ ] `--sigs` JSON prepared (`[r,s,z]` or `{"r","s","z"}`).

## Phase B — the gates

- [ ] `smoothness --n <ord>` for dlog shapes.
- [ ] `Δ = -16(4a³+27b²) mod p` for custom curves.
- [ ] `#E == p` for custom curves.
- [ ] `required_signatures` met for lattice attacks.
- [ ] `--order` is `n`, not `p`.

## Phase C — the solve

- [ ] Cheapest compatible attack first.
- [ ] `hnp-ecdsa` uses `--curve`/`--pubkey` self-verify where possible.
- [ ] `--nonce-bits`/`--nonce-bound` covers `k`.
- [ ] `bsgs`/`pohlig` use `ord(g)`, not `p`.

## Phase D — verify

- [ ] `x·G == Q` or `pow(g, x, p) == h` verified against the *supplied* params.
- [ ] `flag{`/`CTF{` present in the decrypted/forged output.

## Phase E — record

- [ ] `post-probe` with verbatim output.
- [ ] Fail → falsifier in `knowledge/attempts/`.
- [ ] Solve → `classify_solve.py` chain card.
- [ ] Stuck → `decide.py` rungs.
