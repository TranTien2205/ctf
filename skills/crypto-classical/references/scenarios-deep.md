# Scenarios deep — the challenge presentations, annotated

## The "just a blob" challenge

A blob, no name → `cipher_id` → the IC split → the family → `classical_solve`.
The warm-up.

## The "k is given" challenge

`ct` + `k=3` → `caesar --text` — the `k` row — no statistics needed.

## The "the key is hidden" challenge

`ct` + "the key is in the poem/title/image" → extract the word → `vigenere
--key <word>` or `subst`.

## The "a long monoalphabetic" challenge

A long `ct` → `subst --restarts` → the annealed `σ` → near-English → polish
`flag{`.

## The "a scrambled text" challenge

Letters preserved, order scrambled → `railfence`/columnar/route → `π⁻¹` →
`flag{...}`.

## The "nested encoding" challenge

`base64 → caesar → morse → flag` — `cipher_id` on each output.

## The "it's not a cipher" challenge

`+/=`/hex/`01` `ct` → `enc_detect` — an encoding; `flag{` inside.

## The "a named cipher not in the tool" challenge

"we used playfair" → `other-ciphers.md` → a script / dcode.fr.

## The verify

`pt` language + `enc(pt)=ct`.
