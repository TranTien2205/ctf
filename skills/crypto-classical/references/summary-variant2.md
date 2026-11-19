# Summary variant 2 — crypto-classical, by the read

## The read → the family

| The `cipher_id` read | The family | The command |
|---|---|---|
| IC ~0.066, chi² `k` | `caesar` | `classical_solve caesar --text` |
| IC ~0.066, reversed | `atbash` | `classical_solve atbash --text` |
| IC ~0.066, flat | `subst` | `classical_solve subst --text` |
| IC ~0.038, `L` | `vigenere` | `classical_solve vigenere --text --keylen L` |
| IC ~0.05, scrambled | `railfence`/`π` | `classical_solve railfence --text` |

## The `ct`-shape → the tool

| The shape | The tool |
|---|---|
| `+/=`/hex/`01`/`.-` | `enc_detect` |
| `ADFGVX`/`AB`×5 | `other-ciphers`/`playfair-polybius*` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | the crib — `known-plaintext*.md` |
| `n = r·c` | `railfence`/columnar/route |
| a name | `other-ciphers*.md` → a script |

## The families → the files

- `caesar`/`atbash` — `caesar-*.md`,`atbash-*.md`,`shift-variants*.md`.
- `subst` — `subst-*.md`,`monoalphabetic-variants*.md`,`language-scoring*.md`.
- `vigenere` — `vigenere-*.md`,`polyalphabetic-variants*.md`,
  `beaufort-autokey*.md`,`key-length*.md`.
- `railfence` — `railfence-*.md`,`transposition-variants*.md`.
- others — `other-ciphers*.md`,`playfair-polybius*.md`.
- encoding — `encoding-*.md`.

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.

## The honest status

**Catalogue** — no local solve.
