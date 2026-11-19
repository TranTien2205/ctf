# Detection map deep — the observation → file graph, annotated

## The observation layer

- **sigs** → `per-check*.md` dedupe → `ecdsa-nonce-reuse` or `hnp-*`.
- **`h = g^x`** → `smoothness-deep.md` gate → `pohlig-hellman`/`bsgs`.
- **params** → `per-check*.md` `Δ`/`#E` → `smart`/`singular`.
- **oracle** → `recon-order*.md` validation → invalid curve.

## The gate layer

| Gate | File |
|---|---|
| `r` dup | `per-check*.md` |
| `k` bound | `per-boundary*.md` |
| `smoothness` | `smoothness-deep.md` |
| `x` bound | `per-boundary*.md` |
| `Δ`/`#E` | `per-check*.md` |
| validation | `invalid-curve-deep.md` |
| count | `per-boundary*.md` |

## The solve layer

| Attack | Files |
|---|---|
| `ecdsa-nonce-reuse` | `per-attack-ecdsa-nonce-reuse.md`,`ecdsa-nonce-reuse-deep.md` |
| `hnp-ecdsa`/`hnp` | `per-attack-hnp-*.md`,`hnp-*-deep.md` |
| `pohlig-hellman`/`bsgs` | `per-attack-*.md`,`*-deep.md` |
| `smart`/`singular`/`invalid` | `per-attack-*.md`,`*-deep.md` |

## The close layer

| Step | Files |
|---|---|
| verify | `verify*.md` |
| record | `field-notes-*.md`,`evidence*.md` |
| falsify | `falsifiers*.md`,`negative-results*.md` |
| escalate | `decide.py` |
