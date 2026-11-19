# Quick reference — the one-page cheat sheet

## The identify

```bash
cipher_id.py --text 'CT'     # IC/chi²/Kasiski/freq/verdict
enc_detect 'CT'    # the encoding path
```

## The family → the solve

| Signal | Command |
|---|---|
| IC~0.066, one chi² min | `classical_solve caesar --text` |
| IC~0.066, reversed ETAOIN | `classical_solve atbash --text` |
| IC~0.066, flat chi² | `classical_solve subst --text` |
| IC~0.038, `L` | `classical_solve vigenere --text --keylen L` |
| scrambled letters | `classical_solve railfence --text` |
| `+/=`/hex/`01` | `enc_detect` |

## The flags

`--text <CT>` · `--keylen L` (vigenere) · `--key <word>` (vigenere) ·
`--restarts N` (subst) · `--iters N` (subst) · `--selftest`

## The verify

`pt` language + `enc(pt)=ct` + `flag{`/`CTF{` present.

## The falsifiers

- no `k` → `subst`/transposition
- no `L` → `subst`/`π`/other
- no `σ` language → `π`/other
- `+/=`/hex → `enc_detect` — not a cipher
