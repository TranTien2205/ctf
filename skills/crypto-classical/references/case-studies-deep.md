# Case studies deep — the annotated shapes

## The bare blob

`WKHHDWHUHDWGVZQ` — no name, no key. `cipher_id` → IC~0.066, chi² min `k=3` →
`caesar` → `THEEATERATSW...`. The single-shapes are the statistics' job.

## The named cipher

"we used a vigenere cipher with the key LEMON" → `vigenere --key LEMON` — no
statistics needed, the key is given.

## The keyed Vigenere (no key given)

`cipher_id` → IC~0.038, Kasiski `L=5` → `vigenere --keylen 5` → the key
recovered by `L` Caesars.

## The keyworded Vigenere

"the key is a word from the poem" → the obvious words first (`LEMON`,`SECRET`,
the challenge title) before Kasiski — `vigenere --key <word>`.

## The monoalphabetic

`cipher_id` → IC~0.066, flat chi² → `subst` → the annealed `σ` → near-English
→ polish `flag{` positions → `flag{...}`.

## The scrambled text

Right letters, wrong order, length 24 → `railfence` → depth 3 → language.
Or a columnar — brute `w`.

## The layered

`base64(ct) → caesar → morse → flag` — `cipher_id` on each output; the layers
are independent.

## The format-leak

`flag{`/`CTF{` at a position → the format letters pin `σ`/`k`/`key` → confirm
by the decode.

## The verify

`pt` language + `enc(pt)=ct`.
