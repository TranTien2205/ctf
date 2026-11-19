# Negative results — the dead ends, recorded

## The falsifier records

A falsifier hit is a **negative result** — it goes in `knowledge/attempts/` or
`../field-notes.md` so the next attempt doesn't re-walk it.

## The standard negatives

| The negative | The re-route |
|---|---|
| no `k` produces language | `subst`/transposition |
| the reflection produces garbage | `subst` |
| the anneal never reaches language | `π`/other |
| no `L` produces language | `subst`/`π`/other |
| no depth/width produces language | a different `π` or `σ` |
| the multiset isn't English | `π(σ(p))` layered |
| `+/=`/hex/`01` | `enc_detect` — an encoding |

## The short-ct negative

Under ~30 chars the statistics are unreliable — an IC of 0.04 is *not* a
vigenere. The `flag{` positions carry the solve.

## The layered negative

A decode → another `ct` — the first layer's verdict is closed; `cipher_id`
on the output.

## The record

`post-probe --verdict falsifies` or the `knowledge/attempts/` entry.
