# Scenarios variant — the challenge presentations, by shape

## The bare-blob scenario

A blob, no name → `cipher_id` → the IC split → `classical_solve`. The
warm-up.

## The `k`-given scenario

`ct` + "k=3"/"rot"/"shifted" → `caesar --text`, read the `k=3` row.

## The named-cipher scenario

"we used a playfair/adfgvx/hill cipher" → `other-ciphers*.md` → a script —
`cipher_id` confirms the family.

## The keyed-but-unnamed scenario

"the key is a word from the poem/title/image" → `vigenere --key <word>` or
`subst` — the obvious words first.

## The layered scenario

`base64 → caesar → morse → flag` — `cipher_id` per layer.

## The `π(σ(p))` scenario

IC~0.05 but the letters aren't English → un-scramble `π` first → `subst`.

## The encoding-not-cipher scenario

`+/=`/hex/`01` `ct` → `enc_detect` — `flag{` inside.

## The short-blob scenario

Under ~30 chars → the `flag{` positions carry — `known-plaintext*.md`.

## The `n`-composite scenario

`n = r·c` → `railfence`/columnar/route → `transposition-variants*.md`.

## The verify

`pt` language + `enc(pt)=ct`.
