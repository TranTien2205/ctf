# Known-plaintext catalogue — the cribs, indexed

## The crib types

| Crib | What it anchors | The files |
|---|---|---|
| `flag{`/`CTF{`/`HTB{` | `σ`/`k`/`key`/`π` at those positions | `known-plaintext*.md` |
| `SNT{`/`synt{`/`Pxl{`/`fhpnf{` | a `k`-shift — decode the format | `caesar-*.md`,`known-plaintext*.md` |
| `gLAG{`/`fLAG{` | the wrong `σ` entries | `subst-*.md`,`common-questions*.md` |
| a greeting/format | `σ`/`k`/`key` | `known-plaintext*.md` |
| a poem's words | `vigenere`/`subst` key | `known-plaintext*.md`,`vigenere-*.md` |

## The crib → the parameter — per family

| Family | The crib → the parameter |
|---|---|
| `caesar` | `k = ct[i] - 'f'` — one position |
| `vigenere` | `k_{i mod L} = ct[i] - 'f'` — `L` positions |
| `subst` | `σ⁻¹(ct[j]) = 'flag{'[j]` — `σ` anchored |
| `railfence`/`π` | `f` maps to `ct[π⁻¹(i)]` — `π` positions |
| keyed-alphabet | `σ` of `KEYWORD` + the `k` offset |

## The layered crib

The `flag{` is the *innermost* layer — the outer layers' cribs are their own
formats (`+/=` charset, `.-` Morse) — `multi-step-chains*.md`.

## The verify

`enc(pt) == ct` — the crib + the decode confirm — `verify*.md`.
