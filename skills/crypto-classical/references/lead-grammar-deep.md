# Lead grammar deep — the hint → the signal → the file

## The hint → the family → the file

| The hint | The family | The file |
|---|---|---|
| "shifted"/"rot"/"caesar"/"k=N" | `caesar` | `caesar-*.md` |
| "reversed"/"mirrored"/"atbash" | `atbash` | `atbash-*.md` |
| "key word"/"vigenere"/"polyalphabetic" | `vigenere` | `vigenere-*.md` |
| "substituted"/"monoalphabetic"/"scrambled" | `subst` | `subst-*.md` |
| "rails"/"columns"/"transposed"/"reordered" | `railfence`/columnar | `railfence-*.md` |
| "encoded"/"base64"/"hex" | `enc_detect` | `encoding-vs-cipher.md` |
| "playfair"/"digraph"/"square" | `playfair` | `other-ciphers.md`,`playfair-polybius.md` |
| "grid"/"polybius"/"tap" | `polybius` | `playfair-polybius.md` |
| "beaufort"/"autokey" | the reciprocals | `beaufort-autokey.md` |
| "adfgx"/"adfgvx" | `adfgvx` | `other-ciphers.md` |
| "hill"/"matrix" | `hill` | `other-ciphers.md` |

## The text → the family

| In the text | The family | The file |
|---|---|---|
| a cipher name | the decoder | `other-ciphers.md` |
| a "key"/"keyword" | `vigenere`/`subst` | `vigenere-*.md` |
| a "rail"/"fence"/"columns" | `railfence`/columnar | `railfence-*.md` |
| `flag{`/`CTF{`/`SNT{` | the format leak | `known-plaintext.md` |
| `+/=`/hex/`01` | `enc_detect` | `encoding-vs-cipher.md` |

## The falsifier-first rule

`cipher_id` first — the statistics decide; the hint is a lead, not a route.
