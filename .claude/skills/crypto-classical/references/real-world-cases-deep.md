# Real-world cases deep — the CTF presentations, annotated

## The warm-up Caesar

`ct` + "the Romans knew this" → `caesar --text` → `k` → `flag{...}`. The
`chi²` min is `k`.

## The keyed Vigenere

`ct` + "key: LEMON" → `vigenere --key LEMON` → `flag{...}` — the key is in
the text.

## The keyword-Vigenere

`ct` + "the key is a word from the image" → extract → `vigenere --key <word>`.

## The substitution marathon

A long `ct` → `subst --restarts 8 --iters 4000` → the annealed `σ` →
near-English → `flag{...}`.

## The transposition puzzle

A scrambled text → `railfence`/columnar → `flag{...}`.

## The nested chain

`base64 → caesar → morse → flag` — `cipher_id` per layer.

## The encoding-not-cipher

`+/=`/hex/`01` → `enc_detect` → `flag{...}` inside.

## The verify

`pt` language + `enc(pt)=ct` — the flag from the decode.
