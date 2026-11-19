# Detection index variant 3 — the reads indexed by question

## "What is it?" reads

| Question | Files |
|---|---|
| nonce/dlog/defect? | `detection*.md`,`cipher-identification.md` |
| sigs or params? | `detection*.md` |
| oracle or handout? | `detection*.md`,`recon-order*.md` |

## "Which attack?" reads

| Question | Files |
|---|---|
| same `r`? | `per-check*.md` → `ecdsa-nonce-reuse` |
| `k` bounded? | `per-boundary*.md` → `hnp-ecdsa` |
| partial `k`? | `hnp-deep.md` → `hnp` |
| `ord` smooth? | `smoothness-deep.md` → `pohlig-hellman` |
| `x` bounded? | `per-boundary*.md` → `bsgs` |
| `Δ`/`#E`? | `per-check*.md` → `singular`/`smart` |
| unvalidated? | `invalid-curve-deep.md` → invalid curve |

## "How?" reads

| Question | Files |
|---|---|
| the command? | `payload-dictionary*.md` |
| the flags? | `payload-dictionary*.md` |
| the helpers? | `operator-notes*.md` |
| the verify? | `verify*.md`,`per-check*.md` |

## "Dead?" reads

| Question | Files |
|---|---|
| kill condition? | `falsifiers*.md`,`per-falsifier.md` |
| record the no? | `negative-results*.md` |
| next? | `decide.py`,`falsifiers*.md` |
