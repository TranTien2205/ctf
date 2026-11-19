# Workflow playbook deep — procedures with the why

## The signature playbook, annotated

1. **Inventory** — count sigs; `<2` ends nonce work. Dedupe `r` — the reuse
   check is free and highest-value.
2. **Reuse** → `ecdsa-nonce-reuse` — closed form, instant, no lattice. The
   two entries used are the first two in `--sigs`; put the reuse pair first.
3. **Bias** → `hnp-ecdsa` — needs `k < B` uniform + `m ≥ required_signatures`.
   `--nonce-bits B` = `k < 2^B`; `--nonce-bound B` = `k < B` exact.
4. **Partial** → `hnp` — transform `t = s⁻¹r`, `u = -s⁻¹z` per sig.
5. **Verify** — `d·G == Q` before forging/decrypting.

## The dlog playbook, annotated

1. **Smoothness** — `smoothness --n ord` gates the whole branch.
2. **PH** — largest factor ≤ 2⁴⁰ feasible; `--order` = `ord(g)`, and the
   tool computes `ord(g)` itself so a non-generator doesn't slip.
3. **BSGS** — `x < B` stated → `--order B`; else `ord` ≤ 2⁴⁴.
4. **Verify** — `pow(g, x, p) == h`; `pow(h, ord, p) == 1` confirms `h ∈ <g>`.

## The curve playbook, annotated

1. **Δ** — `0` → singular; near-zero is normal.
2. **#E** — `== p` → anomalous; smooth → PH; prime/near-p → generic-hard.
3. **Point ops** — `ec.curve` for custom `(p,a,b)`; `mul/add/point`.
4. **Verify** — `x·G == Q` with supplied `G`, `Q`, `p`, `a`, `b`.

## The oracle playbook, annotated

1. **Determinism** — `sign(m)` ×2: same `(r,s)` → RFC 6979; different →
   random `k`. If deterministic, reuse needs `r` to repeat across *different* `m`.
2. **Validation** — submit off-curve `P'` → accepted → invalid-curve; rejected → closed.
3. **Bias** — collect `≥ required_signatures` sigs if `k` bounded.

## The close playbook, annotated

`post-probe` (evidence = verbatim output) → `../field-notes.md` →
`classify_solve.py` on solve / `knowledge/attempts/` on dead end →
`decide.py` for the next rung.
