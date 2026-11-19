# Probe catalogue deep — the reads → the output, expanded

## The identify reads

| Read | Output | File |
|---|---|---|
| `cipher_id --text` | IC/chi²/Kasiski/freq/verdict | `detection*.md` |
| `enc_detect` | an encoding | `encoding-vs-cipher.md` |
| the charset | cipher vs encoding | `detection.md` |
| a name | the decoder | `other-ciphers.md` |
| `flag{`/`CTF{` | the format leak | `known-plaintext.md` |
| `n = r·c` | a grid | `railfence-*.md` |

## The solve reads — by family

| Read | Output | File |
|---|---|---|
| `caesar --text` | the 25 `k` ranked | `caesar-*.md` |
| `atbash --text` | the reflection | `atbash-*.md` |
| `vigenere --text` | `L` + the key | `vigenere-*.md` |
| `vigenere --keylen L` | the `L`-forced key | `vigenere-*.md` |
| `vigenere --key W` | the `W`-decode | `vigenere-*.md` |
| `subst --text` | the `σ` | `subst-*.md` |
| `subst --restarts` | a harder `σ` | `subst-*.md` |
| `railfence --text` | the depths | `railfence-*.md` |
| a script | the named other | `other-ciphers.md` |
| `enc_detect` | the encoding | `encoding-vs-cipher.md` |

## The verify reads

| Read | Output | File |
|---|---|---|
| the `pt` read | language or `flag{...}` | `verify.md`,`evidence.md` |
| `enc(pt)==ct` | the transform confirmed | `verify.md` |
| `flag{`/`CTF{` present | the flag | `evidence.md` |
