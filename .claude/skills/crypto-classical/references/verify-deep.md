# Verify deep — the solve's checks, annotated

## The re-encrypt check — `enc(pt, param) == ct`

The `k`/`L`/`σ`/depth/key reproduced the ciphertext. A plausible `pt` without
the re-encrypt is a *candidate* — the `σ` anneal can hallucinate.

## The language check — `pt` is language

Words, the `flag{`/`CTF{` format. `gLAG{...}` is a *candidate* — the `flag{`
positions reveal the wrong `σ`/`k`/`L` entries — polish them.

## The flag check — `flag{`/`CTF{` present

`flag{`/`CTF{` in `pt` → the flag. `SNT{`/`synt{`/`Pxl{`/`fhpnf{` → a
ROT13/`k`-shift artifact — decode it back.

## The layered check — per-layer verify

A `pt` that's another `ct` — `cipher_id` on the output. Each layer verifies
`enc(pt)==ct`; the last verifies `flag{` present.

## The partial-decode check — `gLAG{`

A near-decode — a partially-right `σ` — `σ⁻¹(g)` should be `f`. The `flag{`
positions reveal the wrong entries — swap and re-verify.

## The record — the `post-probe`

`post-probe --hypothesis-id <h> --class crypto-classical --verdict confirms
--evidence-kind class --evidence "<the pt>" --response "<the decode output>"`
→ `classify_solve.py --chain <id>` → `../field-notes.md`.
