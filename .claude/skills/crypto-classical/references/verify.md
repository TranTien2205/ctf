# Verify — the solve's two checks

## The re-encrypt check

`enc(pt, param) == ct` — the `k`/`L`/`σ`/depth/key reproduced the ciphertext.
A plausible `pt` without the re-encrypt is a *candidate*.

## The language check

`pt` is language — words, the `flag{`/`CTF{` format. `gLAG{...}` is a
*candidate* — polish the wrong `σ`/`k`/`L` entries.

## The flag check

`flag{`/`CTF{` present in `pt` → the flag. `SNT{`/`synt{`/`Pxl{` → a
ROT13/partial-shift artifact — decode it back.

## The layered check

A `pt` that's another `ct` — `cipher_id` on the output; the verify applies
per-layer, not just the last.

## The record

`post-probe --hypothesis-id --class crypto-classical --verdict confirms
--evidence-kind class --evidence "<the pt>" --response "<the decode output>"`
→ `classify_solve.py --chain <id>` → `../field-notes.md`.
