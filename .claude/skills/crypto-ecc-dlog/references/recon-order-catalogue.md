# Recon order catalogue — the oracle probes → the files

## The recon probes → files

| Probe | Files |
|---|---|
| determinism (`sign(m)` twice) | `recon-order*.md`,`per-check*.md` |
| `r` pattern across sigs | `recon-order*.md`,`per-family-nonce.md` |
| validation (`P'` off-curve) | `recon-order*.md`,`invalid-curve-deep.md` |
| error leakage | `recon-order*.md`,`edge-cases-deep.md` |
| `n`/`ord` from response | `recon-order*.md`,`per-check*.md` |

## The recon order rationale → files

| Why | Files |
|---|---|
| cheapest read first | `recon-order*.md`,`probe-order*.md` |
| validation before attack | `recon-order*.md`,`invalid-curve-deep.md` |
| determinism before nonce | `recon-order*.md`,`per-family-nonce.md` |

## The recon outputs → routes

| Output | Route |
|---|---|
| same `r` | `ecdsa-nonce-reuse` |
| distinct `r`, `k` biased | `hnp-ecdsa` |
| `P'` accepted | invalid curve |
| `P'` rejected | not invalid curve |
| `ord` leaked | `smoothness` gate |
