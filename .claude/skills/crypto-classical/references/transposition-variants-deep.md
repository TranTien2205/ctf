# Transposition variants deep — the `π` shapes, annotated

## Rail-fence — the zigzag `π`

`r` rails; `pt` written `\/` over the rails, read row-major. Depth `r`:
`classical_solve railfence --text` — the `r` ranked.

## Columnar — the key-ordered columns

`w` columns; `pt` written row-major `w` at a time, columns read in `key`
order. `key='ZEBRA'` → rank `Z=3,E=1,B=0,R=2,A=4` → read columns `3,1,0,2,4`.
Brute `w`; a key word names the order.

## Route — a grid path

`n = r·c` grid; `pt` filled row-major, read a path: spiral, zigzag, diagonal,
boustrophedon (snake), knight's tour. The `n` composite is the tell.

## Scytale — the fixed-width wrap

`pt` on a `w`-width ribbon — read down the columns — a `w`-column route with
row read. Brute `w` from 2.

## Block permutation — `b`-block `π`

`pt` split into `b`-blocks; each block permuted by `π` (a `b`-element key =
a permutation of `0..b-1`).

## Permutation cipher — a keyed `π`

`π` a permutation — the key is the perm `key=[2,0,3,1]`.

## The `π(σ(p))` layered — `π` first

A transposition *of* a substituted text — the letters aren't English — the
multiset is the `σ` invariant. Un-scramble `π` (position-only — `railfence`/
columnar by `n`) *first*, then `subst` the un-scrambled `ct`.

## The `σ(π(p))` layered — `σ` first — rarer

`σ` scrambles the letter values, `π` the positions — `subst` first (the `σ`
shape), then `π`.

## The verify

`π(p) == c` — the permutation reproduced.
