# Verify catalogue — the solve's checks, indexed

## The re-encrypt check

`enc(pt, param) == ct` — `verify*.md`,`evidence*.md` — the transform
reproduced.

## The language check

`pt` is language — `verify*.md` — words, the `flag{`/`CTF{` format.

## The flag check

`flag{`/`CTF{` present — `evidence*.md` — `SNT{`/`synt{`/`Pxl{`/`fhpnf{` → a
`k`-shift artifact — decode the format.

## The layered check

A `pt` that's another `ct` — `cipher_id` on the output — `multi-step-chains*.md`
— per-layer verify.

## The partial-decode check — `gLAG{`

A partially-right `σ` — `σ⁻¹(g)` should be `f` — `subst-*.md`,
`common-questions*.md` — swap and re-verify.

## The record

`post-probe --hypothesis-id --class crypto-classical --verdict confirms
--evidence-kind class --evidence "<pt>" --response "<decode>"` →
`classify_solve.py --chain <id>` → `../field-notes.md` —
`evidence*.md`,`field-notes-catalogue.md`.
