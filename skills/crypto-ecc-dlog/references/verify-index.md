# Verify index — the checks → the files

## The primary checks → files

| Check | Files |
|---|---|
| `x·G == Q` | `verify*.md`,`per-check*.md`,`operator-notes*.md` |
| `pow(g,x,p) == h` | `verify*.md`,`per-check*.md` |
| `pow(h,ord,p) == 1` | `per-check*.md` |
| `flag{` grep | `verify*.md`,`evidence*.md` |

## The per-attack checks → files

| Attack | Check | Files |
|---|---|---|
| `ecdsa-nonce-reuse` | `d·G == Q` | `ecdsa-nonce-reuse-deep.md`,`verify*.md` |
| `hnp-ecdsa`/`hnp` | `d·G == Q` | `hnp-*.md`,`verify*.md` |
| `pohlig-hellman` | `g^x == h` | `pohlig-hellman-deep.md`,`verify*.md` |
| `bsgs` | `g^x == h` | `bsgs-deep.md`,`verify*.md` |
| `smart`/`singular` | `x·G == Q` | `smart-attack-deep.md`,`singular-ec-deep.md` |
| invalid curve | `d·G == Q` | `invalid-curve-deep.md` |

## The evidence checks → files

| Check | Files |
|---|---|
| `class` evidence (scalar) | `evidence*.md` |
| `impact` evidence (flag) | `evidence*.md`,`multi-step-chains*.md` |
| `post-probe` shape | `evidence*.md`,`field-notes-*.md` |
