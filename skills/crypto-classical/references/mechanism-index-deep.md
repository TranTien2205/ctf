# Mechanism index deep — the primitives → the files, annotated

## The transform primitives → the family files

| Primitive | The transform | The family | The files |
|---|---|---|---|
| `c = p + k` | a cyclic shift | `caesar`/ROT | `caesar-*.md`,`shift-variants*.md` |
| `c = 25 - p` | a reflection | `atbash` | `atbash-*.md` |
| `c = σ(p)` | a bijection | `subst`/affine/keyword | `subst-*.md`,`monoalphabetic-variants*.md` |
| `c = (a·p+b) mod 26` | a linear `σ` | `affine` | `monoalphabetic-variants*.md` |
| `c_i = p_i + k_{i mod L}` | `L` cycling shifts | `vigenere`/beaufort/autokey/gronsfeld | `vigenere-*.md`,`polyalphabetic-variants*.md` |
| `c = π(p)` | a position-permutation | `railfence`/columnar/route/scytale | `railfence-*.md`,`transposition-variants*.md` |
| `c = M p mod 26` | a matrix | `hill` | `other-ciphers*.md` |
| `c = digraph(p_i,p_j)` | a keyed square | `playfair` | `playfair-polybius*.md` |
| `c = (row,col)(p)` | a fractionation | `polybius`/adfgvx | `playfair-polybius*.md` |
| `c = enc(p)` | a structured code | base64/hex/morse/baconian | `encoding-*.md`,`other-ciphers*.md` |

## The statistic primitives → the files

| Statistic | Reads | The files |
|---|---|---|
| IC | the collision prob | `detection-deep.md`,`theory*.md`,`frequency-analysis*.md` |
| chi² | the `k` fit | `detection-deep.md`,`caesar-*.md` |
| Kasiski | the `L` period | `key-length*.md`,`vigenere-*.md` |
| tetragram | the `σ` objective | `language-scoring*.md`,`subst-*.md` |
| frequency | the letter shape | `frequency-analysis*.md` |
| charset | the enc/cipher split | `detection.md`,`encoding-*.md` |
| digraphs | `σ`-preserved/`π`-broken | `frequency-analysis*.md`,`playfair-polybius*.md` |
| coset | the `L`-subsequence | `key-length*.md`,`vigenere-*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
