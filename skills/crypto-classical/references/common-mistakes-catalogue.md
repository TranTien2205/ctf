# Common mistakes catalogue — the errors, indexed

## The discrimination errors

| Mistake | The fix | File |
|---|---|---|
| encoding as a cipher | `enc_detect` — the charset first | `common-mistakes*.md`,`encoding-*.md` |
| anneal a polyalpha | `cipher_id` first — IC ~0.038 | `common-mistakes*.md`,`vigenere-*.md` |
| `σ`/`π` confusion | the *order* — `π` scrambles, `σ` renames | `common-mistakes*.md`,`railfence-*.md` |
| short-ct over-trust | the `flag{` positions carry | `edge-cases*.md`,`common-questions*.md` |

## The solve errors

| Mistake | The fix | File |
|---|---|---|
| near-decode as flag | `gLAG{` — polish the `σ` | `subst-*.md`,`evidence*.md` |
| re-run a falsified family | change family — the falsifier is a signal | `falsifiers*.md` |
| the `L` mis-estimate | `L`/`L/2`/`2L` — the coset-IC | `key-length*.md`,`vigenere-*.md` |
| keyed-alphabet blind | `subst` solves `σ` regardless | `subst-*.md` |
| `π(σ(p))` order | un-scramble `π` first | `railfence-*.md`,`multi-step-chains*.md` |

## The verify errors

| Mistake | The fix | File |
|---|---|---|
| unverified read | `enc(pt)==ct` | `verify*.md`,`evidence*.md` |
| `synt{` as the flag | decode the format (ROT13) | `caesar-*.md` |
| layered re-attack | `cipher_id` on the output | `multi-step-chains*.md` |
