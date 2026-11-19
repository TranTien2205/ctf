# Attack shapes — the composed business-logic exploits

`exploitation-shapes.md` names the single-edge geometries. This module
is the composed attacks — how the edges stack into flag-reaching
chains.

## Compose: mass assignment → role → gated surface → flag

```
edge 1:  POST /register {..., "role":"admin"}   → role:admin
edge 2:  GET /admin/users                        → 200 (role gate opens)
edge 3:  GET /admin/config | /admin/flag         → flag field
```

The role is reach, not sink — the flag lives in what the role unlocks.
Probe the whole admin surface from the bundle's route table, not one
guessed path.

## Compose: boundary → negative total → checkout → flag

```
edge 1:  POST /cart {qty:-1}                    → total:-50
edge 2:  POST /checkout                          → charged:-50 / refunded:50
edge 3:  GET /flag                               → flag on the anomalous
                                                  ledger state
```

The negative cart is the class confirm; the checkout accepting it is
the impact. In challenge design the flag is often priced above legit
max — buy it with the credited balance.

## Compose: replay → doubled credit → purchase → flag

```
edge 1:  POST /redeem ×2                         → balance:+100 not +50
edge 2:  POST /buy {"item":"flag"}               → balance covers it
edge 3:  GET /inventory                          → flag item owned
```

Replay is the credit primitive; the flag is an overpriced item. The
"flag" in shops is usually a product at 10× max legit balance.

## Compose: workflow skip → terminal state → flag

```
edge 1:  POST /confirm (no /pay)                 → confirmed+unpaid
edge 2:  GET /order/N                            → flag field in
                                                  confirmed order
```

Or: skip → `/activate` bare → `verified:true` → gated endpoint.

## Compose: transform gap → controlled write → privileged instruction

The Pachinko geometry:

```
edge 1:  id=<past doc limit> → different-layer rejection (transform
         confirmed unchecked)
edge 2:  compute id: off + id*S mod 2^w → instruction memory
edge 3:  write privileged instruction at the wrap address
edge 4:  CPU executes it before halt → flag output/state
```

Generalized: any checked-index reaching a transformed address — the
write primitive's target decides the impact (code overwrite, adjacent
object corruption, flag-field write).

## Compose: trust → carried lie → downstream grant

```
edge 1:  step1 response mints {"price":50}
edge 2:  POST /order {"price":1,"item":"flag"}   → charged:1 for flag item
edge 3:  GET /order → flag item shipped
```

## Compose: singleton → second privileged object → flag

```
edge 1:  POST /admin (or /flag-holder create) ×2 → second privileged
edge 2:  the second instance's default state carries the flag
```

## The chain-walk discipline

Each edge is its own hypothesis with its own probe/baseline/evidence —
the chain is assembled from recorded edges, not assumed from the first
confirm. When edge N falsifies, the chain reroutes through the OTHER
mechanisms that state reaches — the state machine is a graph, and
`s_flag` usually has multiple incoming edges.
