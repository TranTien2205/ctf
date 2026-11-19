# Per-boundary map — the boundary conditions → the class they bound

## The solvable boundary

| The boundary | The class inside it |
|---|---|
| a reachable transition to the predicate's state exists | ANY of the classes — the solve is that transition |
| every reachable writer of the predicate's slot is guarded + unbypassable | NO class — the contract is closed |
| the supplied caller can deploy contracts | the contract-in-middle classes (tx.origin, reentrancy, phish, force) |
| the chain is a private testnet | the instance-scoped solve — the attributable caller is supplied |

## The per-class boundary table

| Class | Inside the boundary | Outside |
|---|---|---|
| access-control | an unguarded/bypassable writer | every writer guarded + unbypassable |
| reentrancy | `call`-then-update + a controllable callee | `.transfer`/`send`/`nonReentrant`/CEI |
| delegatecall | a controlled/mismatched target | no delegatecall / fixed + matching |
| storage-collision | a `delegatecall` + a layout mismatch | layouts verified matching / EIP-1967 |
| tx.origin | a `tx.origin` check + a contract-in-chain | `msg.sender` correct + no contract path |
| integer-overflow | `<0.8` or `unchecked` + a wrapping path | `>=0.8` + SafeMath + no unchecked |
| weak-randomness | a `block.*`/readable decision | commit-reveal / VRF / no predictable source |
| selfdestruct | a `selfdestruct` reachable / a balance predicate | no selfdestruct + a non-balance predicate |
| uninitialized-proxy | a callable `initialize` | initialized + protected in both contexts |
| front-running | an ordering-dependent decision | commit-reveal / not ordering-sensitive |
| signature | a replayable/malleable/zero-addr hash | a fully-bound hash + low-s + `!=0` check |
| accounting | a desync path | every in/out atomic, no donation/reentrancy |
| visibility | a `private`/`internal`/event/log "secret" | the secret is genuinely off-chain |
| gas-griefing | a push-payment/unbounded-loop the contract needs | pull-payment / bounded / the revert tolerated |

## The "the boundary is the falsifier" note

Each class's boundary is its falsifier — `falsifiers.md` + `per-falsifier.md`
record them. A falsifier observed → the class is closed → `decide.py escalate`.

## The "the boundary is the solve" note

A challenge is solvable exactly when SOME class's inside-boundary holds — a
reachable transition flips the predicate. The reachable-writers enumeration is
the boundary-test for the whole class.
