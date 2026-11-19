# Mechanism catalogue — the primitives, indexed

## The transform primitives

| Primitive | The transform | The family |
|---|---|---|
| `c = p + k mod 26` | a cyclic shift | `caesar`/ROT |
| `c = 25 - p` | a reflection | `atbash` |
| `c = σ(p)` | a bijection | `subst`/affine/keyword |
| `c_i = p_i + k_{i mod L}` | `L` cycling shifts | `vigenere`/beaufort/autokey |
| `c = π(p)` | a position-permutation | `railfence`/columnar/route |
| `c = enc(p)` | a structured code | base64/hex/morse/baconian |

## The statistic primitives

| Statistic | What it reads | The files |
|---|---|---|
| IC | the collision probability | `detection-deep.md`,`theory*.md` |
| chi² | the `k` fit | `detection-deep.md`,`caesar-*.md` |
| Kasiski | the `L` period | `key-length*.md`,`vigenere-*.md` |
| tetragram | the `σ` objective | `language-scoring*.md`,`subst-*.md` |
| frequency | the letter shape | `frequency-analysis*.md` |
| charset | the enc/cipher split | `detection.md`,`encoding-*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
