# Detection playbook map — procedure → file → command

## The inventory → file → command

| Step | File | Command |
|---|---|---|
| artifact type | `detection*.md` | — |
| group naming | `recon-order.md` | `ec.curve(...)` |
| sig inventory | `detection*.md` | — |

## The discriminate → file → command

| Step | File | Command |
|---|---|---|
| `r` dedupe | `per-check*.md` | `Counter(r)` |
| `ord` factor | `smoothness-deep.md` | `smoothness --n ord` |
| `Δ` check | `per-check*.md` | `4a³+27b² mod p` |
| `#E` check | `per-check*.md` | `E.order()` |
| `h ∈ <g>` check | `per-check*.md` | `pow(h, ord, p)` |
| count check | `per-boundary*.md` | `required_signatures` |

## The solve → file → command

| Step | File | Command |
|---|---|---|
| reuse | `per-attack-ecdsa-nonce-reuse.md` | `ecdsa-nonce-reuse --sigs --order` |
| bias | `per-attack-hnp-ecdsa.md` | `hnp-ecdsa --sigs --order --nonce-*` |
| raw HNP | `per-attack-hnp.md` | `hnp --t --u --modulus --bound` |
| smooth dlog | `per-attack-pohlig-hellman.md` | `pohlig-hellman --g --h --p --order` |
| bounded dlog | `per-attack-bsgs.md` | `bsgs --g --h --p --order` |
| anomalous | `per-attack-smart.md` | `tools/crypto/smart_attack.py` |
| singular | `per-attack-singular.md` | `tools/crypto/singular_ec.py` |
| invalid | `per-attack-invalid-curve.md` | `tools/crypto/ec.py` + `bsgs`/`pohlig` |

## The verify → file → command

| Step | File | Command |
|---|---|---|
| `d·G == Q` | `verify*.md` | `ec.py` |
| `g^x == h` | `verify*.md` | `pow(g, x, p)` |
| flag | `evidence*.md` | decrypt/forge |
