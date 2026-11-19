# Transposition variants — the `π` shapes

## Rail-fence — the zigzag

`r` rails; `pt` written in a zigzag, read row-major. `classical_solve
railfence --text` tries the depths.

## Columnar — the key-ordered columns

`w` columns; `pt` written row-major, columns read in `key` order.
`key = 'ZEBRA'` → column order `3,1,0,2,4` (alphabetical rank).

## Route — a grid path

`n = r·c` grid; `pt` filled row-major, read in a spiral / zigzag / diagonal /
boustrophedon. The grid shape is the tell — `n` composite.

## Scytale — a fixed-width wrap

`pt` on a `w`-width ribbon — read down the columns — a `w`-column route with
row read. Brute `w`.

## Block permutation — `b`-block `π`

`pt` split into `b`-blocks; each block permuted by `π` (a `b`-element key).
`key` a permutation of `0..b-1`.

## The `π(σ(p))` layered

A transposition of a substituted text — the letters aren't English — un-
scramble `π` (position-only), then `subst`.

## The `σ(π(p))` layered — rarer

`σ` scrambles the letter *values*, `π` the positions — the solve order depends
on which the `cipher_id` stats surface.

## The verify

`π(p) == c` — the permutation reproduced.
