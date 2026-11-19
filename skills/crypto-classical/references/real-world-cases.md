# Real-world cases — the CTF presentations

## The "solve a caesar" challenge

`ct` + a name → `classical_solve caesar` → `flag{...}`. The warm-up.

## The "find the key" vigenere

`ct`, no key → `cipher_id` (IC~0.038, Kasiski `L`) → `vigenere --keylen` →
the key + `flag{...}`.

## The substitution marathon

A long monoalphabetic → `subst --restarts` → the annealed `σ` → near-English →
polish `flag{`.

## The transposition puzzle

A scrambled text, letters preserved → `railfence`/columnar → `flag{...}`.

## The nested chain

`base64 → caesar → vigenere → flag` — the `cipher_id` call on each layer.

## The encoding-not-cipher

`+/=`/hex/`01` → `enc_detect.py` — a `flag{` inside the decoded text.

## The verify

`pt` language + `enc(pt)=ct`.
