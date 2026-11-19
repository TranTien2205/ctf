# Troubleshoot catalogue deep — the failure → the fix, indexed, annotated

## The discriminate failures

| Failure | The fix | The files |
|---|---|---|
| `cipher_id` wrong family | `flag{` positions; a layered `ct` → on output | `troubleshoot-deep.md`,`edge-cases*.md` |
| IC near 0.05 — mono or poly | the `flag{` positions / `π` | `edge-cases*.md`,`common-questions*.md` |
| flat chi² — `subst` or `π` | the *order* — `π` scrambles, `σ` renames | `subst-*.md`,`railfence-*.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers`/`playfair-polybius*` | `other-ciphers*.md` |

## The `caesar` failures

| Failure | The fix | The files |
|---|---|---|
| `caesar` gives garbage | `subst`/`π`; strip non-letters; a keyed `σ` | `caesar-*.md`,`troubleshoot-deep.md` |
| a keyed alphabet | `subst` on the `k`-shifted output | `subst-*.md` |
| `synt{`/`Pxl{`/`fhpnf{` | decode the format — `k`-shift | `caesar-*.md` |

## The `subst` failures

| Failure | The fix | The files |
|---|---|---|
| the anneal plateaus | `π`/other; `--restarts`/`--iters`; `flag{` anchor | `subst-*.md`,`per-falsifier*.md` |
| `gLAG{` | the `flag{` positions pin `σ` | `subst-*.md`,`common-questions*.md` |
| the `ct` too short | the `flag{` positions / a crib | `known-plaintext*.md` |
| `π(σ(p))` | un-scramble `π` first | `railfence-*.md`,`multi-step-chains*.md` |

## The `vigenere` failures

| Failure | The fix | The files |
|---|---|---|
| `vigenere` gives garbage | `L`/`L/2`/`2L`; `c=k-p`; autokey; `subst` | `vigenere-*.md`,`beaufort-autokey*.md` |
| Kasiski reads no `L` | autokey (`key=primer+pt`) or `subst`/`π` | `beaufort-autokey*.md` |

## The `railfence`/`π` failures

| Failure | The fix | The files |
|---|---|---|
| `railfence` gives garbage | columnar `w`; route; `σ` | `railfence-*.md`,`troubleshoot-deep.md` |
| `n` not a grid | `σ`/`k`, not `π` | `railfence-*.md` |

## The layered failures

| Failure | The fix | The files |
|---|---|---|
| decode → another `ct` | `cipher_id` on the output | `multi-step-chains*.md` |
| `enc_detect` on a cipher | a `σ` — `cipher_id` reads it | `encoding-*.md` |
