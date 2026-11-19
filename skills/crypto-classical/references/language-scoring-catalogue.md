# Language scoring catalogue — the `subst` objective, indexed

## The model

`score(σ) = Σ_i log p_4(pt[i:i+4])` — the tetragram sum — `subst-*.md`,
`language-scoring*.md`.

## The anneal — the `subst` procedure

| Step | The file |
|---|---|
| init by frequency | `language-scoring*.md`,`frequency-analysis*.md` |
| score the `σ`-decode | `language-scoring*.md` |
| swap two `σ` entries | `language-scoring*.md` |
| keep the improvement | `language-scoring*.md` |
| `--restarts`/`--iters` | `language-scoring*.md`,`payload-dictionary*.md` |

## The polish — `gLAG{`

A partially-right `σ` — the `flag{`/`CTF{` positions reveal the wrong `σ`
entries — `subst-*.md`,`common-questions*.md`,`known-plaintext*.md`.

## The short-ct problem

Under ~100 chars the tetragram model is weak — the `flag{`/`CTF{` positions
or a crib carry the solve — `known-plaintext*.md`,`edge-cases*.md`.

## The keyed-alphabet read

`σ = KEYWORD + rest` — the keyword in `σ`'s order —
`monoalphabetic-variants*.md`,`subst-*.md`.

## The falsifier

The score plateaus below language — not a `σ` → `π`/other —
`per-falsifier*.md`.
