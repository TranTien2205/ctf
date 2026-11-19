# Railfence catalogue deep — the `π` family, fully indexed

## The family — `c = π(p)`

A permutation of *positions* — the multiset exactly preserved; IC ~0.05-0.066,
English counts, scrambled order.

## The variants — the `π` set

| Variant | The `π` | The solve | The files |
|---|---|---|---|
| rail-fence | a `r`-rail zigzag | `railfence --text` the depths | `railfence-deep.md`,`railfence-catalogue.md` |
| columnar | `w` columns key-ordered | brute `w` / a key word | `railfence-*.md`,`transposition-variants*.md` |
| route | a `n=r·c` grid path | a script — spiral/zigzag/diagonal | `transposition-variants*.md` |
| scytale | a `w`-width wrap | brute `w` | `transposition-variants*.md` |
| block-perm | a `b`-block `π` | a `b`-key perm | `transposition-variants*.md` |
| permutation cipher | a keyed `π` | a `0..b-1` perm | `transposition-variants*.md` |

## The `π(σ(p))` layered — `π` first

A transposition *of* a substituted text — the letters aren't English.
Un-scramble `π` (position-only — `railfence`/columnar by `n`) *first*, then
`subst` the un-scrambled `ct` — `multi-step-chains*.md`.

## The `σ(π(p))` layered — `σ` first — rarer

`σ` scrambles the letter values, `π` the positions — `subst` first → `π`.

## The detection — the preserved multiset

IC ~0.05-0.066 — English letter counts, scrambled order — the freq is
English, the text garbage. `n` composite → a grid.

## The solve — `π`'s shape

`railfence --text` (depths) / a script (columnar/route/scytale/block).

## The verify

`π(p) == c` — the permutation reproduced.
