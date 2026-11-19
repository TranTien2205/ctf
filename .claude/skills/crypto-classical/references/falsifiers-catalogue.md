# Falsifiers catalogue — the closes, indexed

## The family falsifiers

| Family | The falsifier | The re-route | The files |
|---|---|---|---|
| `caesar` | no `k` produces language | `subst`/transposition | `caesar-*.md`,`per-falsifier*.md` |
| `atbash` | the reflection is garbage | `subst` | `atbash-*.md`,`per-falsifier*.md` |
| `subst` | the anneal never reaches language | `π`/other | `subst-*.md`,`per-falsifier*.md` |
| `vigenere` | no `L` produces language | `subst`/`π`/other; `c=k-p` | `vigenere-*.md`,`per-falsifier*.md` |
| `railfence` | no depth/width produces language | a different `π` or `σ` | `railfence-*.md`,`per-falsifier*.md` |
| `π` | the multiset isn't English | `π(σ(p))` layered | `railfence-*.md`,`edge-cases*.md` |

## The boundary falsifiers

| Signal | The close | The files |
|---|---|---|
| `+/=`/hex/`01`/`.-`/`/` | `enc_detect` — an encoding | `detection.md`,`encoding-*.md` |
| `ADFGVX`/`AB`×5 | `other-ciphers` — a script | `other-ciphers.md`,`playfair-polybius*.md` |
| letters-only | a cipher — the stats apply | `cipher-identification.md` |
| `flag{`/`CTF{`/`SNT{` | the format leak — a cipher | `known-plaintext*.md` |

## The shape falsifiers

| The falsifier | The re-route | The files |
|---|---|---|
| short `ct` — stats unreliable | the `flag{` positions carry | `edge-cases*.md`,`common-questions*.md` |
| layered `ct` — first layer closed | `cipher_id` on the output | `multi-step-chains*.md` |
| `σ` over keyed alphabet | `subst` on the output | `subst-*.md` |
| the `L` mis-estimate | `L`/`L/2`/`2L` | `key-length*.md` |

## The honest-status falsifier

**Catalogue** — a skill recommendation is a *lead*, not a confirmation —
`verified-chains*.md`.
