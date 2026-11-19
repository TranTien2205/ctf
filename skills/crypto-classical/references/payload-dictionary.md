# Payload dictionary — the `classical_solve` invocations

## The identify

```bash
python3 tools/cipher_id.py --text 'CT'          # IC/chi²/Kasiski/freq/verdict
python3 tools/enc_detect.py ''CT'         # the encoding path
```

## The family solvers — `classical_solve <family> --text <CT>`

```bash
python3 tools/classical_solve.py caesar --text 'CT'
#   → the 25 k ranked by chi²; the min is k

python3 tools/classical_solve.py atbash --text 'CT'
#   → the reflection c=25-p

python3 tools/classical_solve.py vigenere --text 'CT'
#   → IC/Kasiski → L → L Caesars → the key + pt

python3 tools/classical_solve.py vigenere --text 'CT' --keylen 5
#   → force L=5

python3 tools/classical_solve.py vigenere --text 'CT' --key LEMON
#   → a known key

python3 tools/classical_solve.py subst --text 'CT'
#   → the tetragram anneal → σ → pt

python3 tools/classical_solve.py subst --text 'CT' --restarts 8 --iters 4000
#   → more anneal work for a harder σ

python3 tools/classical_solve.py railfence --text 'CT'
#   → the rail depths ranked

python3 tools/classical_solve.py <family> --selftest
#   → the offline self-test
```

## The named others — not in the tool

`other-ciphers.md` — playfair, affine, polybius, baconian, beaufort, autokey,
gronsfeld, adfgx, hill — a script / dcode.fr.

## The verify

`pt` language + `enc(pt)=ct` — the `k`/`L`/`σ`/depth proven.
