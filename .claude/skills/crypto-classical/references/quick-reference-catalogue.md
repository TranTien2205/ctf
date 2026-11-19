# Quick reference catalogue — the cheat sheets, indexed

## The identify

| Command | The output | File |
|---|---|---|
| `cipher_id --text` | IC/chi²/Kasiski/freq/verdict | `detection*.md` |
| `enc_detect` | an encoding | `encoding-*.md` |
| `classical_solve <f> --selftest` | the tool works | `preconditions.md` |

## The family → the solve — the quick table

| Signal | Command | File |
|---|---|---|
| IC~0.066, chi² `k` | `classical_solve caesar --text` | `caesar-*.md` |
| IC~0.066, reversed | `classical_solve atbash --text` | `atbash-*.md` |
| IC~0.066, flat | `classical_solve subst --text` | `subst-*.md` |
| IC~0.038, `L` | `classical_solve vigenere --text --keylen L` | `vigenere-*.md` |
| IC~0.05, scrambled | `classical_solve railfence --text` | `railfence-*.md` |
| `+/=`/hex/`01`/`.-` | `enc_detect` | `encoding-*.md` |
| a name | `other-ciphers.md` → a script | `other-ciphers*.md` |
| `flag{` positions | `known-plaintext.md` → the crib | `known-plaintext*.md` |
| `n = r·c` | `railfence`/columnar/route | `railfence-*.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers`/`playfair-polybius*` | `playfair-polybius*.md` |

## The flags — `classical_solve`

`--text` · `--keylen` · `--key` · `--restarts` · `--iters` · `--selftest` —
`payload-dictionary*.md`.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present — `verify*.md`.
