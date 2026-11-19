# Field manual deep — the procedures, annotated

## The discriminate procedure

`cipher_id.py --text` → the IC/chi²/Kasiski/freq → `cipher-identification.md`
→ the family. The charset first — `enc_detect` before the cipher statistics.

## The cheap-solve procedure — cost order

`atbash` (the reflection, one op) → `caesar` (25 `k`) → `vigenere` (Kasiski
`L`, `L` Caesars) → `railfence` (the depths) → `subst` (the anneal — slowest)
→ the named others (a script).

## The polish procedure — a near-decode

`gLAG{...}` / a near-English `subst` — the `flag{`/`CTF{` positions reveal the
wrong `σ`/`k`/`L` entries — `σ⁻¹(g)` should be `f` — swap and re-score.

## The nested procedure — a layered cipher

A decode → another `ct` — `cipher_id` on the *output*, not a re-attack on the
first layer. `base64 → caesar → morse → flag`.

## The named-cipher procedure

A name in the text — "we used playfair" — `other-ciphers.md` → a script /
dcode.fr — `cipher_id` still reads the family.

## The verify procedure

`pt` language → `enc(pt) == ct` → `flag{`/`CTF{` present → the flag.

## The record procedure

`post-probe --hypothesis-id --class --verdict --evidence-kind --evidence
--response` · `classify_solve.py --chain <id>` · `../field-notes.md` ·
`knowledge/attempts/` for a dead end.
