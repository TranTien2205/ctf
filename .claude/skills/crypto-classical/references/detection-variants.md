# Detection variants — the reads, by challenge shape

## The bare blob

`cipher_id --text` → the IC split → the family → `classical_solve`.

## The named cipher

A name in the text → `classical_solve <family>` or `other-ciphers.md` → a
script.

## The keyed-but-unnamed

"key"/"keyword" → `vigenere`/`subst` — the obvious words first, then Kasiski.

## The layered blob

`cipher_id` → layer → decode → `cipher_id` on the output → repeat.

## The encoding blob

`+/=`/hex/`01` → `enc_detect` → the decoded text → `cipher_id` if a `ct`
remains.

## The short blob

Under ~30 chars → the `flag{`/`CTF{` positions + common letters anchor
`σ`/`k`/`key` — the stats unreliable.

## The `n`-composite blob

`n = r·c` → a grid → `railfence`/columnar/route.

## The `flag{`-visible blob

`flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{` — the format leak anchors the transform.

## The mixed-charset blob

letters+digits → a partial cipher — letters transformed, digits kept.

## The verify

`pt` language + `enc(pt)=ct`.
