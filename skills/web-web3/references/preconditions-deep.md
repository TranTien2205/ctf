# Preconditions (deep) — what each class needs, with the check

## The universal precondition — the reachable transition

The class needs a reachable transition — a function the supplied caller (or a
contract they deploy) can call whose post-state satisfies `isSolved()`. The
check is the reachable-writers enumeration: every non-view external/public
function listed, each checked for a write to the predicate's slots. If NONE is
reachable, the class is closed — `per-falsifier.md`.

## Per-class preconditions with the check

| Class | The precondition | The check |
|---|---|---|
| access-control | an unguarded/bypassable writer of the predicate's slot | `grep` the setters; `cast call` the getter; the guard's form |
| reentrancy | a `call`-then-update + a controllable callee | `grep call` — the call type; a `receive`-hook contract deployable |
| delegatecall | a `delegatecall` to an influenceable/mismatched target | `grep delegatecall`; `cast storage` the impl slot |
| storage-collision | the delegatecall + a layout mismatch | diff the proxy/impl slot declarations |
| tx.origin | a `tx.origin` check + a deployable contract | `grep tx.origin`; the caller deploys a Phish |
| integer-overflow | `<0.8` or `unchecked` + a wrapping path | `grep pragma` + `grep unchecked`/`SafeMath` |
| weak-randomness | a `block.*`/readable decision source | `grep block.`/`blockhash`/`timestamp`/`private` |
| selfdestruct | a `selfdestruct` reachable OR a balance-predicate | `grep selfdestruct`; the predicate's form |
| uninitialized-proxy | a callable `initialize` in the impl/proxy context | `grep initialize`; `cast call` the `initialized` flag |
| front-running | an ordering-dependent decision | the claim/winner/auction shape |
| signature | an `ecrecover` + a replayable/malleable hash | `grep ecrecover`; read the hash's bound fields |
| accounting | a desync path in the tracked value | the deposit/withdraw/rate shape |
| visibility | a `private`/`internal`/event/log "secret" the predicate needs | `grep private`/`internal`; `cast storage` |
| gas-griefing | a push-payment/unbounded-loop the contract needs | `grep for`/`while`/`transfer`/`call` the dependent fn |
| token-standards | the token's surface — a custom path the challenge trusts | the token's functions + the consumer's assumption |
| flashloan-oracle | a manipulable source the decision reads | the `getPrice`/`reserve`/`balanceOf` source |

## The instance precondition

The exploit needs the LIVE per-instance values — the RPC, the key, the deployed
addresses. `cast chain-id` + `cast wallet address` + `cast call $SETUP` confirm
the live instance; stale values from a dead instance fail.

## The funding precondition

A `payable`/`ether`-needing exploit needs the supplied caller funded —
`cast balance $ME`. A contract-deploy exploit needs the deploy to carry
`--value` or a `payable` constructor + a funding call.

## The tooling precondition

`cast`/`forge`/`solc` (or `web3`/`ethers`/`python`) — `which cast forge solc`.
A bytecode-only target needs `evm`/`heimdall`/`panoramix` to decompile.
