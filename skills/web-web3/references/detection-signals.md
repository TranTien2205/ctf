# Detection signals — the observable → the class signal strength

## The strong signals (name the class)

| Signal | Class | Strength |
|---|---|---|
| `isSolved()` reading `owner()` | access-control family | strong |
| `isSolved()` reading `balance` | drain family | strong |
| `delegatecall` in the code | delegatecall/collision | strong |
| `tx.origin` in a check | tx.origin | strong |
| `call{value}` before a `-=` | reentrancy | strong |
| `pragma ^0.4-^0.7`, no SafeMath | integer-overflow | strong |
| `block.*` in a decision | weak-randomness | strong |
| `selfdestruct` | selfdestruct family | strong |
| `ecrecover` | signature | strong |
| `initialize`/`init` | uninitialized-proxy | strong |
| a bare `setOwner`/`unlock`/`setFlag` | access-control | strong |

## The weak signals (suggest, don't name)

| Signal | Suggests | Verify |
|---|---|---|
| a `fallback`/`receive` | the entry — what's callable | read its body |
| `payable` | an ether path | is it exploitable? |
| `private`/`internal` | a "secret" | is it in the predicate? `cast storage` |
| a `for`/`while` | a loop | is it over a growing set? |
| `keccak256`/`sha3` | a hash — sig/answer/commit | what's hashed? |
| `transfer`/`withdraw` | a payout | is it reenter-able? |
| `import`/`library` | a shared dep | `delegatecall` into it? |
| a `modifier`/`onlyX` | a guard | bypassable? |

## The negative signals (close the class)

| Signal | Closes |
|---|---|
| `.transfer`/`.send` only | reentrancy |
| `nonReentrant` on every state-sharing fn | reentrancy |
| `>=0.8` + SafeMath, no `unchecked` | integer-overflow |
| `initialized` true | uninitialized-proxy |
| commit-reveal / VRF | weak-randomness |
| the predicate's slots unreachable | the whole class |

## The order

The strong source signals name the class; the weak signals suggest; the
negative signals close. `isSolved()`'s predicate is the STRONGEST signal —
read it first; it aims the whole detection.
