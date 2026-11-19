# Payload dictionary deep — the invocations, annotated

## The identify

```bash
python3 tools/cipher_id.py --text 'CT'          # IC/chi²/Kasiski/freq/verdict
python3 tools/cipher_id.py --selftest           # the offline self-test
python3 tools/enc_detect.py ''CT'         # the encoding path
```

## `caesar` — the shift

```bash
classical_solve caesar --text 'CT'   # the 25 k ranked by chi²
# → k produces language; re-shift pt by k == ct
```

## `atbash` — the reflection

```bash
classical_solve atbash --text 'CT'   # c = 25 - p
```

## `vigenere` — the polyalphabetic

```bash
classical_solve vigenere --text 'CT'               # IC/Kasiski → L → key
classical_solve vigenere --text 'CT' --keylen 5    # force L
classical_solve vigenere --text 'CT' --key LEMON   # a known key
```

## `subst` — the monoalphabetic

```bash
classical_solve subst --text 'CT'                            # the anneal
classical_solve subst --text 'CT' --restarts 8 --iters 4000  # harder σ
```

## `railfence` — the transposition

```bash
classical_solve railfence --text 'CT'   # the depths ranked
```

## The named others — `other-ciphers.md`

`classical_solve` doesn't cover playfair/affine/polybius/baconian/beaufort/
autokey/gronsfeld/adfgx/hill — a script / dcode.fr.

## The verify

`pt` language + `enc(pt)=ct` — the `k`/`L`/`σ`/depth proven.
