# Quick reference deep — the one-page cheat sheet, expanded

## The identify

```bash
cipher_id.py --text 'CT'          # IC/chi²/Kasiski/freq/verdict
enc_detect 'CT'         # the encoding path
classical_solve.py <f> --selftest # the tool works
```

## The family → the solve

| Signal | Command |
|---|---|
| IC~0.066, one chi² min | `classical_solve caesar --text` |
| IC~0.066, reversed ETAOIN | `classical_solve atbash --text` |
| IC~0.066, flat chi² | `classical_solve subst --text` |
| IC~0.038, `L` | `classical_solve vigenere --text --keylen L` |
| IC~0.05, scrambled | `classical_solve railfence --text` |
| `+/=`/hex/`01`/`.-` | `enc_detect` |
| a name | `other-ciphers.md` → a script |
| `flag{` positions | `known-plaintext.md` → the crib |

## The flags — `classical_solve`

`--text <CT>` · `--keylen L` (vigenere) · `--key <word>` (vigenere) ·
`--restarts N` (subst) · `--iters N` (subst) · `--selftest`

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.

## The falsifiers

- no `k` → `subst`/transposition
- no `L` → `subst`/`π`/other
- no `σ` language → `π`/other
- no depth/width → a different `π` or `σ`
- `+/=`/hex → `enc_detect` — not a cipher

## The record

`post-probe` · `classify_solve.py` · `../field-notes.md` · `knowledge/attempts/`.
