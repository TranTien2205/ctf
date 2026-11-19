# Per-family index — the families → the files, annotated

## The monoalpha families

| Family | The files | The command |
|---|---|---|
| `caesar`/ROT | `caesar-*.md`,`shift-variants*.md` | `classical_solve caesar --text` |
| `atbash` | `atbash-*.md` | `classical_solve atbash --text` |
| `subst` | `subst-*.md`,`monoalphabetic-variants*.md` | `classical_solve subst --text` |
| affine | `monoalphabetic-variants*.md` | `subst`/a script |

## The polyalpha families

| Family | The files | The command |
|---|---|---|
| `vigenere` | `vigenere-*.md` | `classical_solve vigenere --text` |
| beaufort/autokey | `beaufort-autokey*.md`,`polyalphabetic-variants*.md` | `vigenere`/a script |
| gronsfeld/keyed-alphabet | `polyalphabetic-variants*.md` | `vigenere` + `subst` |

## The transposition families

| Family | The files | The command |
|---|---|---|
| `railfence` | `railfence-*.md` | `classical_solve railfence --text` |
| columnar/route/scytale | `transposition-variants*.md` | a grid / a script |
| `π(σ(p))`/`σ(π(p))` | `multi-step-chains*.md` | `π`/`σ` order |

## The named others

| Family | The files | The command |
|---|---|---|
| playfair/polybius | `playfair-polybius*.md` | a script |
| adfgvx/bifid | `other-ciphers*.md` | a script |
| hill | `other-ciphers*.md` | a script |

## The encoding boundary

| Family | The files | The command |
|---|---|---|
| base64/hex/morse/baconian | `encoding-*.md`,`other-ciphers*.md` | `enc_detect` |
