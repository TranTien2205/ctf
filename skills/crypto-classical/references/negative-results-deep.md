# Negative results deep — the dead ends, recorded, annotated

## The falsifier records

A falsifier hit is a **negative result** — it goes in `knowledge/attempts/` or
`../field-notes.md` so the next attempt doesn't re-walk it. A falsifier is a
*signal*, not a suggestion to try harder.

## The standard negatives — by family

| The negative | The re-route |
|---|---|
| no `k` produces language | `subst`/transposition |
| the reflection produces garbage | `subst` |
| the anneal never reaches language | `π`/other |
| no `L` produces language | `subst`/`π`/other; `c=k-p` |
| no depth/width produces language | a different `π` or `σ` |
| the multiset isn't English | `π(σ(p))` layered |
| `+/=`/hex/`01` | `enc_detect` — an encoding |
| `ADFGVX`/`AB`×5 | `other-ciphers` — a script |

## The short-ct negative

Under ~30 chars the statistics are unreliable — an IC of 0.04 is *not* a
vigenere. The `flag{`/`CTF{` positions carry the solve — `known-plaintext.md`.

## The layered negative

A decode → another `ct` — the first layer's verdict is closed; `cipher_id`
on the output — a *new* `ct`, a new read.

## The `π(σ(p))` negative

`subst` on a scrambled `ct` fails — the `σ` operates on the un-scrambled
letters. Un-scramble `π` (position-only) first, then `subst`.

## The record

`post-probe --verdict falsifies` → `knowledge/attempts/<challenge>.json` —
the falsifier recorded, not re-walked.
