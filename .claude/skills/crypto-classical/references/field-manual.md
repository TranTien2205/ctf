# Field manual — the procedures

## The discriminate procedure

`cipher_id.py --text` → the IC/chi²/Kasiski → `cipher-identification.md` →
the family.

## The cheap-solve procedure

`caesar` (25 `k`) → `atbash` → `vigenere` (Kasiski `L`, `L` Caesars) →
`railfence` (depths) → `subst` (annealing — slower) — cost order.

## The polish procedure

A near-decode → the flag-shaped positions → the wrong `σ`/`k`/`L` entries →
swap/re-estimate → `flag{...}`.

## The nested procedure

A decode → another ciphertext → `cipher_id` on the output → the next layer.

## The verify procedure

`pt` language → `enc(pt)==ct` → `flag{`/`CTF{` present → the flag.

## The record procedure

`post-probe --hypothesis-id --class --verdict --evidence-kind --evidence
--response` · `classify_solve.py --chain <id>` · `../field-notes.md` ·
`knowledge/attempts/` for a dead end.
