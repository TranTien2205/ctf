# Workflow variant — the order, by challenge shape

## The named-cipher shape

A name in the text → skip `cipher_id` → `classical_solve <family>` or a
script → verify.

## The bare-blob shape

`cipher_id` → the IC split → the family → `classical_solve` → verify.

## The keyed-but-unnamed shape

A "key"/"keyword" hint → `vigenere`/`subst` — the obvious words first, then
Kasiski.

## The layered shape

`cipher_id` → layer → decode → `cipher_id` on the output → repeat → `flag`.

## The encoding shape

`+/=`/hex/`01` → `enc_detect` → the decoded text → `cipher_id` if a `ct`
remains.

## The short-blob shape

Under ~30 chars → the `flag{` positions + common letters anchor `σ`/`k`/`key`
→ `classical_solve` polishes.

## The verify

`pt` language + `enc(pt)=ct` — every shape ends at the verify.
