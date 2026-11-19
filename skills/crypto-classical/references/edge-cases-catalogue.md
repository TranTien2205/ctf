# Edge cases catalogue — the boundary forms, fully indexed

## The degenerate transforms

| Case | The files |
|---|---|
| `k=0` (`c=p`) | `edge-cases*.md`,`boundary-cases*.md` |
| `L=1` (Vigenere = Caesar) | `key-length*.md`,`boundary-cases*.md` |
| `L=n` (single-period) | `key-length*.md` |
| `a=1,b=0` (Affine = identity) | `boundary-cases*.md` |
| `σ=identity` / `σ` a swap | `boundary-cases*.md`,`subst-*.md` |
| `k=13` (ROT13) | `caesar-*.md`,`shift-variants.md` |

## The length edges

| Case | The files |
|---|---|
| `n < 30` | `edge-cases*.md`,`boundary-cases*.md`,`common-questions*.md` |
| `n` composite `r·c` | `railfence-*.md`,`transposition-variants*.md` |
| `n` square | `railfence-*.md` |
| `n` prime | `boundary-cases*.md` |

## The charset edges

| Case | The files |
|---|---|
| letters+digits | `edge-cases*.md`,`detection-surface*.md` |
| spaces kept | `edge-cases*.md` |
| mixed case | `edge-cases*.md`,`detection-surface*.md` |
| `flag{`/`CTF{`/`SNT{`/`synt{`/`Pxl{`/`fhpnf{` | `known-plaintext*.md`,`detection*.md` |

## The layered edges

| Case | The files |
|---|---|
| `π(σ(p))` — `π` first | `railfence-*.md`,`multi-step-chains*.md` |
| `σ(π(p))` — `σ` first | `multi-step-chains*.md` |
| `enc → cipher → enc` | `multi-step-chains*.md`,`encoding-*.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
