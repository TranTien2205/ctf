# Boundary cases catalogue — the edge forms, indexed

## The degenerate transforms

| Case | The files |
|---|---|
| `k=0` / `L=1` / `a=1,b=0` / `σ=identity` | `boundary-cases*.md`,`edge-cases*.md` |
| `k=13` ROT13 | `caesar-*.md`,`shift-variants.md` |
| `L=n` a single-period | `key-length*.md`,`boundary-cases*.md` |
| `σ` a two-letter swap | `subst-*.md`,`boundary-cases*.md` |

## The length edges

| Case | The files |
|---|---|
| `n < 30` short | `edge-cases*.md`,`boundary-cases*.md`,`common-questions*.md` |
| `n` composite `r·c` | `railfence-*.md`,`transposition-variants*.md` |
| `n` square | `railfence-*.md`,`transposition-variants*.md` |
| `n` prime | `boundary-cases*.md`,`edge-cases*.md` |

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
| `base64 → caesar → morse` | `multi-step-chains*.md`,`encoding-boundary.md` |

## The verify

`pt` language + `enc(pt)=ct` — `verify*.md`.
