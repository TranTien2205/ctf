# Mechanism surface — the transforms, one-glance

## The four transforms

| Transform | The family | The `cipher_id` read |
|---|---|---|
| `c = p + k` | `caesar`/ROT | IC~0.066, chi² `k` |
| `c = 25 - p` | `atbash` | IC~0.066, reversed ETAOIN |
| `c = σ(p)` | `subst`/affine/keyword | IC~0.066, flat chi², ETAOIN |
| `c_i = p_i + k_{i mod L}` | `vigenere`/beaufort/autokey | IC~0.038, Kasiski `L` |
| `c = π(p)` | `railfence`/columnar/route | IC~0.05-0.066, scrambled |
| `c = enc(p)` | base64/hex/morse/baconian | the charset |

## The compositions

| Composition | The order |
|---|---|
| `π(σ(p))` | `π` first, then `subst` |
| `σ(π(p))` | `σ` first, then `π` |
| keyed-alphabet Vigenere | `vigenere` `L`, then `subst` |
| `enc → cipher → enc` | `enc_detect`/`cipher_id` per layer |

## The verify

`pt` language + `enc(pt)=ct`.
