# Mechanism variant 2 — the transforms, by composition

## The simple transforms — one op

| Transform | The family |
|---|---|
| `c = p + k` | `caesar`/ROT |
| `c = 25 - p` | `atbash` |
| `c = σ(p)` | `subst`/affine/keyword |
| `c_i = p_i + k_{i mod L}` | `vigenere`/beaufort/autokey/gronsfeld |
| `c = π(p)` | `railfence`/columnar/route/scytale |
| `c = enc(p)` | base64/hex/morse/baconian |

## The composed transforms — `π`/`σ`/`k`/`L` chains

| Composition | The order | The files |
|---|---|---|
| `π(σ(p))` | `π` first (position-only), then `subst` | `railfence-*.md`,`multi-step-chains*.md` |
| `σ(π(p))` | `σ` first, then `π` | `multi-step-chains*.md` |
| keyed-alphabet Vigenere | `vigenere` `L`, then `subst` per-coset | `vigenere-*.md`,`multi-step-chains*.md` |
| `enc → cipher → enc` | `enc_detect`/`cipher_id` per layer | `multi-step-chains*.md`,`encoding-*.md` |
| `cipher → enc` | `cipher_id` → `classical_solve` → `enc_detect` | `multi-step-chains*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md` — per-layer for a composition.
