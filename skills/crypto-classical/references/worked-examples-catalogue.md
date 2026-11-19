# Worked examples catalogue — the solves, indexed

## The single-cipher examples

| Example | The family | The file |
|---|---|---|
| Caesar `k=3` | `caesar` | `worked-examples*.md`,`caesar-*.md` |
| Vigenere `LEMON` | `vigenere` | `worked-examples*.md`,`vigenere-*.md` |
| subst `σ` | `subst` | `worked-examples*.md`,`subst-*.md` |
| rail-fence `r=3` | `railfence` | `worked-examples*.md`,`railfence-*.md` |
| atbash | `atbash` | `worked-examples*.md`,`atbash-*.md` |

## The crib examples

| Example | The file |
|---|---|
| `flag{` at a position → `σ`/`k`/`key` | `known-plaintext*.md`,`worked-examples*.md` |
| `synt{`/`Pxl{`/`fhpnf{` → decode the format | `caesar-*.md`,`worked-examples*.md` |
| `gLAG{` → the `flag{` positions pin `σ` | `subst-*.md`,`worked-examples*.md` |

## The layered examples

| Example | The file |
|---|---|
| `base64 → caesar → morse → flag` | `worked-examples*.md`,`multi-step-chains*.md` |
| `π(σ(p))` — `π` first | `railfence-*.md`,`worked-examples*.md` |
| keyed-alphabet Vigenere → `subst` | `vigenere-*.md`,`multi-step-chains*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
