# Mechanism map — the primitive → the family → the file

| Primitive | Family | File |
|---|---|---|
| `c = p + k` | shift | `caesar-*` |
| `c = 25 - p` | reflection | `atbash-*` |
| `c = σ(p)` | bijection | `subst-*` |
| `c_i = p_i + k_{i mod L}` | polyalpha | `vigenere-*` |
| `c = π(p)` | permutation | `railfence-*` |
| `+/=`/hex/`01`/`.-` | encoding | `detection.md`,`class-boundary.md` |
| a keyed square / digraphs | named other | `other-ciphers.md` |

## The statistics → the family

| Statistic | Reads | File |
|---|---|---|
| IC | the mono/poly split | `detection*.md` |
| chi² | the `k` | `caesar-*.md` |
| Kasiski | the `L` | `vigenere-*.md` |
| frequency | the shape | `subst-*.md`,`atbash-*.md` |
| charset | the enc/cipher split | `detection.md` |
