# Payload dictionary variant — the invocations, by family

## The identify — `cipher_id`/`enc_detect`

```bash
cipher_id.py --text 'CT'     # IC/chi²/Kasiski/freq/verdict
cipher_id.py --selftest
enc_detect 'CT'    # the encoding path
enc_detect.py --selftest
```

## `caesar` — the shift

```bash
classical_solve caesar --text 'CT'   # the 25 k ranked
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

`playfair`/`affine`/`polybius`/`baconian`/`beaufort`/`autokey`/`gronsfeld`/
`adfgvx`/`hill` — a script / dcode.fr — `playfair-polybius*.md`.

## The verify

`pt` language + `enc(pt)=ct` — the `k`/`L`/`σ`/depth/`key` proven.
