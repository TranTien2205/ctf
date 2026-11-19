# Verified chains index — the honest status → the files

## The honest status

`verified-chains*.md`,`operator-checklist.md` — **catalogue**, no local solve.

## The verified-chain components — as a pattern

| Component | The files |
|---|---|
| the class's read | `detection*.md`,`cipher-identification.md` |
| the tuple → the family | `detection-matrix*.md`,`per-family-*.md` |
| the family → `classical_solve` | `payload-dictionary*.md`,`workflow*.md` |
| the verify | `verify*.md`,`evidence*.md` |
| the falsifier | `falsifiers*.md`,`per-falsifier*.md` |

## The chains the class *would* produce

| Chain | The files |
|---|---|
| `caesar`/`atbash` | `caesar-*.md`,`atbash-*.md` |
| `subst` | `subst-*.md`,`monoalphabetic-variants*.md` |
| `vigenere`/beaufort/autokey | `vigenere-*.md`,`polyalphabetic-variants*.md` |
| `railfence`/columnar/route | `railfence-*.md`,`transposition-variants*.md` |
| playfair/adfgvx/hill | `other-ciphers*.md`,`playfair-polybius*.md` |
| `enc → cipher → enc` | `multi-step-chains*.md` |
| `π(σ(p))`/`σ(π(p))` | `multi-step-chains*.md` |

## The evidence a card would need

`evidence*.md`,`verify*.md` — the `ct`, the `cipher_id` tuple, the `pt`, the
`flag`, `enc(pt)=ct`.
