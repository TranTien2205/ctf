# Evidence deep — what a solve counts as, annotated

## The standard

A classical solve counts when `enc(pt) == ct` and `pt` is language — the
transform reproduced the ciphertext. `flag{`/`CTF{` present is the flag.

## The evidence ladder

| Stage | What it is | The status |
|---|---|---|
| a chi² minimum | a candidate `k` | candidate |
| an `L` from Kasiski | a candidate period | candidate |
| an annealed `σ` | a candidate `σ` | candidate |
| a near-decode `gLAG{` | a partially-right `σ` | candidate |
| `enc(pt)==ct`, `pt` language | the transform proven | confirm |
| `flag{`/`CTF{` present | the flag | flag |

## The confirms — the `enc(pt)==ct` rule

- **`k`** → `c = p + k` reproduces `ct` → `caesar` confirmed.
- **`L` + `key`** → `c_i = p_i + k_{i mod L}` reproduces `ct` → `vigenere`.
- **`σ`** → `c = σ(p)` reproduces `ct` → `subst` confirmed.
- **depth/`w`/`π`** → `c = π(p)` reproduces `ct` → `railfence`/transposition.
- **the reflection** → `c = 25 - p` reproduces `ct` → `atbash`.

## The `post-probe` record

`post-probe --hypothesis-id <h> --class crypto-classical --verdict confirms
--evidence-kind class --evidence "<the pt>" --response "<the decode output>"`

## The honest status

**Catalogue** — no local solve. `../field-notes.md` for real solves; a confirm
promotes the class.
