# Multi-step chains catalogue — the composite decodes, indexed

## The layered chains

| Chain | The files |
|---|---|
| `enc → cipher → enc → flag` | `multi-step-chains*.md`,`worked-examples*.md` |
| `base64 → caesar → morse → flag` | `multi-step-chains*.md` |
| `enc → cipher` | `multi-step-chains*.md`,`encoding-vs-cipher.md` |

## The cipher-composition chains

| Chain | The files |
|---|---|
| `vigenere → subst` (keyed alphabet) | `multi-step-chains*.md`,`vigenere-*.md` |
| `π(σ(p))` — `π` first | `railfence-*.md`,`multi-step-chains*.md` |
| `σ(π(p))` — `σ` first | `multi-step-chains*.md` |
| `subst → caesar` | `multi-step-chains*.md` |

## The format-leak chains

| Chain | The files |
|---|---|
| `flag{`/`CTF{` → `σ`/`k`/`key` → decode | `known-plaintext.md`,`multi-step-chains*.md` |
| `SNT{`/`synt{`/`Pxl{` → decode the format | `caesar-*.md` |

## The verify — per-layer

Each layer: `enc(pt) == ct`; the last: `flag{` present — `verify*.md`,
`evidence*.md`.
