# Falsifiers deep — what closes each family, annotated

## The family falsifiers

| Family | The falsifier | The re-route |
|---|---|---|
| `caesar` | no `k` in 25 produces language | `subst`/transposition |
| `atbash` | the reflection produces garbage | `subst` |
| `subst` | the anneal never reaches language | `π`/other |
| `vigenere` | no `L` produces language | `subst`/`π`/other; `c=k-p` |
| `railfence` | no depth/width produces language | a different `π` or `σ` |
| transposition | the multiset *isn't* English | `π(σ(p))` layered |

## The boundary falsifier — encoding vs cipher

| The signal | The close |
|---|---|
| `+/=`/hex/`01`/`.-`/`/` | `enc_detect` — an encoding, not a cipher |
| `ADFGVX`/`AB`×5 | `other-ciphers` — a fractionation/Baconian |
| letters-only, no spaces | a cipher — the statistics apply |
| `flag{`/`CTF{`/`SNT{` | the format leak — a cipher |

## The short-ct falsifier

Under ~30 chars the statistics are unreliable — an IC of 0.04 on a 15-char `ct`
is not a `vigenere`; it's a short text. The `flag{` positions carry the solve.

## The layered falsifier

A decode that yields another `ct` — a layered cipher. `cipher_id` on the
output; the first layer's verdict is closed.

## The honest-status falsifier

This is a **catalogue** class — a skill recommendation is a *lead*, not a
confirmation. The decode verifies.

## The record

`post-probe --verdict falsifies` → `knowledge/attempts/<challenge>.json` —
the falsifier recorded, not re-walked.
