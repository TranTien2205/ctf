# Lead grammar — the hint → the signal

## The hint → the family

| The hint | The family |
|---|---|
| "shifted"/"rot"/"caesar"/"k=N" | `caesar` |
| "key word"/"vigenere"/"polyalphabetic" | `vigenere` |
| "substituted"/"monoalphabetic"/"scrambled letters" | `subst` |
| "rails"/"columns"/"transposed"/"reordered" | `railfence`/columnar |
| "reversed"/"mirrored"/"atbash" | `atbash` |
| "encoded"/"base64"/"hex" | `enc_detect` — not a cipher |

## The text → the family

| In the text | The family |
|---|---|
| a cipher name | the decoder |
| a "key"/"keyword" | `vigenere`/`subst` |
| a "rails"/"fence"/"columns" | `railfence`/columnar |
| `flag{`/`CTF{` | the format leak |

## The falsifier-first rule

`cipher_id` first — the statistics decide; the hint is a lead, not a route.
