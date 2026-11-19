# Workflow variant 2 — the order, by the entry signal

## The `cipher_id`-positive entry

IC ~0.066 → monoalpha; ~0.038 → polyalpha; ~0.05 → `π`. The stats → the
family → `classical_solve`.

## The `enc_detect`-positive entry

`+/=`/hex/`01`/`.-` → `enc_detect` → the decoded text → `cipher_id` if a
`ct` remains.

## The `flag{`-visible entry

`flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` → the crib →
`known-plaintext.md` → `classical_solve` confirms.

## The `n`-composite entry

`n = r·c` → a grid → `railfence`/columnar/route → `transposition-variants*.md`.

## The named entry

A cipher name → `other-ciphers.md` → a script — `cipher_id` confirms the
family.

## The keyed entry

A "key"/"keyword" hint → `vigenere`/`subst` — the obvious words first.

## The layered entry

`cipher_id` → layer → decode → `cipher_id` on the output → repeat.

## The verify

`pt` language + `enc(pt)=ct` — every entry ends at the verify.
