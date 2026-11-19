# Mechanism index — the primitives → the files

## The transform primitives

| Primitive | The transform | The files |
|---|---|---|
| `c = p + k mod 26` | a cyclic shift | `caesar-*.md`,`shift-variants*.md` |
| `c = 25 - p` | a reflection | `atbash-*.md` |
| `c = σ(p)` | a bijection | `subst-*.md`,`monoalphabetic-variants*.md` |
| `c_i = p_i + k_{i mod L}` | `L` cycling shifts | `vigenere-*.md`,`polyalphabetic-variants*.md` |
| `c = π(p)` | a position-permutation | `railfence-*.md`,`transposition-variants*.md` |
| `c = enc(p)` | a structured code | `encoding-*.md`,`other-ciphers*.md` |
| `c = (a·p+b) mod 26` | a linear `σ` | `monoalphabetic-variants*.md` |
| `c = M p mod 26` | a matrix | `other-ciphers*.md` |
| `c = digraph(p_i,p_j)` | a keyed square | `playfair-polybius*.md` |
| `c = (row,col)(p)` | a fractionation | `playfair-polybius*.md` |

## The statistic primitives

| Statistic | Reads | The files |
|---|---|---|
| IC | the collision prob | `detection-deep.md`,`theory*.md` |
| chi² | the `k` fit | `detection-deep.md`,`caesar-*.md` |
| Kasiski | the `L` period | `key-length*.md`,`vigenere-*.md` |
| tetragram | the `σ` objective | `language-scoring*.md`,`subst-*.md` |
| frequency | the letter shape | `frequency-analysis*.md` |
| charset | the enc/cipher split | `detection.md`,`encoding-*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
