# Preconditions catalogue — the requirements → the files

## The nonce requirements → files

| Requirement | Files |
|---|---|
| ≥2 sigs | `preconditions*.md`,`per-condition*.md` |
| `r` dup | `preconditions*.md`,`per-check*.md` |
| `m ≥ required` | `preconditions*.md`,`per-boundary*.md` |
| `k_i < B` ∀i | `preconditions*.md`,`per-check*.md` |
| `z`/`t`/`u` derived | `preconditions*.md`,`operator-notes*.md` |

## The dlog requirements → files

| Requirement | Files |
|---|---|
| `ord` smooth | `preconditions*.md`,`smoothness-deep.md` |
| `x`/`ord` bounded | `preconditions*.md`,`bsgs-deep.md` |
| `h ∈ <g>` | `preconditions*.md`,`per-check*.md` |

## The defect requirements → files

| Requirement | Files |
|---|---|
| `#E == p` exact | `preconditions*.md`,`smart-attack-deep.md` |
| `Δ == 0` exact | `preconditions*.md`,`singular-ec-deep.md` |
| `P`,`Q` nonsingular | `preconditions*.md`,`singular-ec-deep.md` |
| no validation | `preconditions*.md`,`invalid-curve-deep.md` |

## The meta requirements → files

| Requirement | Files |
|---|---|
| `--order = n` | `preconditions*.md`,`common-mistakes*.md` |
| `--sigs` file | `preconditions*.md`,`operator-notes*.md` |
| `z`/`ord` correct | `preconditions*.md`,`per-check*.md` |
