# Railfence variants — the `π` family, annotated

## The family

`c = π(p)` — a permutation of *positions*, not letters. The letter multiset is
exactly preserved — IC ~0.05-0.066 — the `ct` has English counts but scrambled
order.

## The variants

### Rail-fence — the zigzag

`r` rails; `pt` written in a zigzag `\/`, read row-major.
`classical_solve railfence --text` — the depths ranked.

### Columnar — the key-ordered columns

`w` columns; `pt` written row-major, columns read in `key` order.
`key='ZEBRA'` → column order `3,1,0,2,4` (alphabetical rank). Brute `w`.

### Route — a grid path

`n = r·c` grid; `pt` filled row-major, read a spiral / zigzag / diagonal /
boustrophedon path.

### Scytale — a fixed-width wrap

`pt` on a `w`-width ribbon, read down columns — a `w`-column route. Brute `w`.

### Block permutation — `b`-block `π`

`pt` in `b`-blocks, each permuted by `π` (a `b`-element key).

### Permutation cipher — a keyed `π`

`π` a permutation of `0..b-1` — the key is the perm.

## The `π(σ(p))` layered — `π` first

A transposition of a substituted text — the letters aren't English.
Un-scramble `π` (position-only) *first* → `subst` the un-scrambled `ct`.

## The `σ(π(p))` layered — `σ` first

`σ` scrambles the letter values, `π` the positions — `subst` first → `π`.

## The detection — the preserved multiset

IC ~0.05-0.066 — the `ct` has English letter counts but scrambled order.
`n` composite → a grid.

## The solve

`railfence --text` (depths) / a script (columnar/route/scytale/block).

## The verify

`π(p) == c` — the permutation reproduced.
