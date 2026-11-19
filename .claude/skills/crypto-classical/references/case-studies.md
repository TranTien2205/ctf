# Case studies — the annotated solve shapes

## The bare blob

`WKHHDWHUHDWGVZQ` — no name, no key. `cipher_id` → IC~0.066, chi² min `k=3`
→ `caesar` → `THEEATERATSW...`. The statistics do the work.

## The named cipher

"we used a vigenere cipher with the key LEMON" → `vigenere --key LEMON` — the
key is given; the statistics aren't needed.

## The keyed Vigenere (no key)

`cipher_id` → IC~0.038, Kasiski `L=5` → `vigenere --keylen 5` → `L` cosets →
`L` Caesars → the key + `pt`.

## The monoalphabetic

`cipher_id` → IC~0.066, flat chi² → `subst` → the annealed `σ` → near-English
→ polish `flag{` positions → `flag{...}`.

## The scrambled text

Right letters, wrong order, length 24 → `railfence` → depth 3 → language.
Or a columnar — brute `w`.

## The layered

`base64(ct) → caesar → morse → flag` — `cipher_id` on each output.

## The format-leak

`flag{`/`CTF{` at a position → the format letters pin `σ`/`k`/`key` → the
decode confirms.

## The verify

`pt` language + `enc(pt)=ct`.
