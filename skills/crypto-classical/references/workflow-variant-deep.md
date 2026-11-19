# Workflow variant deep — the order, by challenge shape, annotated

## The named-cipher shape — "we used a playfair"

A name in the text → `other-ciphers.md`/`playfair-polybius.md` → a script /
dcode.fr → verify. `cipher_id` still confirms the family (IC, the digraph
shape).

## The bare-blob shape — no name, no key

`cipher_id` → the IC split → the family → `classical_solve <f>` → verify.
The standard.

## The keyed-but-unnamed shape — "the key is hidden"

A "key"/"keyword" hint → `vigenere`/`subst` — the obvious words first
(`LEMON`,`SECRET`, the title), then Kasiski/anneal.

## The layered shape — `enc → cipher → enc`

`cipher_id` → layer → decode → `cipher_id` on the output → repeat → `flag`.
`base64 → caesar → morse → flag`.

## The encoding shape — `+/=`/hex/`01`

`enc_detect` → the decoded text → `cipher_id` if a `ct` remains → the family.

## The short-blob shape — under ~30 chars

The `flag{`/`CTF{` positions + common letters anchor `σ`/`k`/`key` →
`classical_solve` polishes — the stats unreliable.

## The `n`-composite shape — a grid

`n = r·c` → `railfence`/columnar/route — the `π` shape.

## The verify

`pt` language + `enc(pt)=ct` — every shape ends at the verify.
