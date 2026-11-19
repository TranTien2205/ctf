# Payload dictionary index — the commands → the files

## The command files

| File | Carries |
|---|---|
| `payload-dictionary.md` | every command + flag |
| `payload-dictionary-deep.md` | the commands + when each |
| `payload-dictionary-variant.md` | compact command card |
| `payload-dictionary-index.md` | this index |

## The per-attack commands → files

| Attack | Command files |
|---|---|
| `ecdsa-nonce-reuse` | `per-attack-ecdsa-nonce-reuse*.md`,`payload-dictionary*.md` |
| `hnp-ecdsa` | `per-attack-hnp-ecdsa*.md`,`payload-dictionary*.md` |
| `hnp` | `per-attack-hnp*.md`,`payload-dictionary*.md` |
| `pohlig-hellman` | `per-attack-pohlig-hellman*.md`,`payload-dictionary*.md` |
| `bsgs` | `per-attack-bsgs*.md`,`payload-dictionary*.md` |
| `smoothness` | `per-attack-smoothness*.md`,`payload-dictionary*.md` |
| `smart`/`singular`/`invalid` | `per-attack-*.md`,`payload-dictionary*.md` |

## The helper commands → files

| Helper | Files |
|---|---|
| `ec.py`/`dlog.py`/`hnp.py` | `payload-dictionary*.md`,`operator-notes*.md` |
| `sigs.json` writer | `operator-notes*.md`,`payload-dictionary-deep.md` |
| `t`/`u` transform | `operator-notes*.md`,`hnp-deep.md` |
| `z` derivation | `operator-notes*.md`,`per-check*.md` |

## The verify commands → files

| Verify | Files |
|---|---|
| `x·G == Q` | `verify*.md`,`operator-notes*.md` |
| `pow(g,x,p) == h` | `verify*.md`,`operator-notes*.md` |
