# Multi-step chains deep — the composite decodes, annotated

## The layered chain — `enc → cipher → enc → flag`

`ct` → `cipher_id` ("encoding") → `enc_detect` → a `caesar` `ct` →
`cipher_id` ("caesar") → `caesar` → a `morse` `ct` → `enc_detect` →
`flag{...}` — `cipher_id` on each output; the layers are independent.

## The `vigenere → subst` chain — a keyed-alphabet Vigenere

`cipher_id` → `vigenere` (the `L` cosets + `k` shifts) → the decoded output is
a `σ`-monoalphabetic (the `k` was over a `KEYWORD` alphabet) → `subst` on the
output → `flag{...}`.

## The `subst → π` chain — `π(σ(p))`

A scrambled *and* substituted text — the multiset is the `σ` invariant:
un-scramble `π` (position-only — rail-fence/columnar by `n`) → `subst` the
un-scrambled `ct` → `flag{...}`.

## The `σ → π` chain — `σ(π(p))` — rarer

`σ` scrambles the letter values, `π` the positions — `subst` first (the `σ`
shape) → un-scramble `π`.

## The `enc → cipher` chain

`enc_detect` → base64/hex → a `cipher_id`-positive output → `classical_solve`
→ `flag{...}`.

## The format-leak chain

`flag{`/`CTF{` at a position → the `σ`/`k`/`key` candidates → the decode
confirms → `flag{...}`.

## The verify — per-layer

Each layer: `enc(pt) == ct`; the last: `flag{` present.
