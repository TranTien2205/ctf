# Multi-step chains — the composite decodes

## The layered chain

`ct` → `cipher_id` (layer 1) → decode → `cipher_id` (layer 2) → decode →
`flag{...}` — `cipher_id` on each output.

## The Vigenere → subst chain

`cipher_id` → `vigenere` (the period+key) → the decoded monoalphabetic →
`subst` on it → `flag{...}` — a Vigenere over a keyed alphabet.

## The subst → transposition chain

A scrambled *and* substituted text → decode the transposition first (the
letters are the multiset) → `subst` on the un-scrambled → `flag{...}`.

## The encoding → cipher chain

`enc_detect` → base64/hex → a `cipher_id`-positive output → `classical_solve`
→ `flag{...}`.

## The format-leak chain

`flag{`/`CTF{` positions → the `σ`/`k`/`key` candidates → the decode confirms
→ `flag{...}`.

## The verify

Each layer asserts — `enc(pt)==ct` for the transform; `flag{` present at the
end.
