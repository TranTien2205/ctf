# Detection matrix — predicate × primitive → the class

## The matrix

| Predicate reads ↓ / Contract has → | `delegatecall` | `call{value}` | `tx.origin` | `block.*` | `selfdestruct` | bare setter | `private` var | arithmetic |
|---|---|---|---|---|---|---|---|---|
| `owner()` | storage-collision | — | tx.origin | — | — | access-control | — | — |
| `balance`/`address(this).balance` | — | reentrancy | — | — | force-feed | — | — | accounting |
| `flag`/`locked`/`solved` | collision → flag slot | — | origin sets flag | — | — | access-control | visibility | — |
| `count`/`balances[x]` | — | reentrancy | — | — | — | — | — | integer-overflow |
| `winner`/`answer`/`guess` | — | — | — | weak-randomness | — | — | visibility | — |
| `code.length`/`extcodesize` | — | — | — | — | selfdestruct | — | — | — |
| `price`/`rate`/`shares` | — | reentrancy | — | weak-randomness | donation | — | — | accounting/flash |
| `signer`/`verified` | — | — | — | — | — | — | — | signature |
| `locked`/`operational` | — | — | — | — | selfdestruct | access-control | — | gas-griefing |

## Reading the matrix

1. the predicate (row) narrows to the classes whose transition changes that state
2. the contract's primitives (column) narrow further — the bug needs the primitive
3. the intersection is the candidate class; `detection-map.md` + the per-bug
   file confirm the reachable transition

## The "no intersection" case

A predicate whose slots have NO reachable writer, on a contract whose primitives
don't enable any class → the challenge's path is a different contract in the
setup, or a different predicate reading. Re-read `isSolved()` and every contract
the setup deploys.
