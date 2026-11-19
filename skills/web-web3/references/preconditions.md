# Preconditions — what each web3 bug needs to be true

## Per-class preconditions

| Class | Needs |
|---|---|
| access-control | a reachable non-view function that writes the predicate's slot, callable by the supplied caller (unguarded, or a bypassable guard) |
| reentrancy | an external `call`/`call{value}` to attacker code BEFORE the state settles; the callee controllable; >2300 gas forwarded |
| delegatecall | a `delegatecall` whose target is influenceable, OR a proxy/impl storage mismatch; a callable path that reaches it |
| storage-collision | a `delegatecall` + a declared-layout mismatch — an impl write lands on a proxy protected slot |
| tx.origin | a `tx.origin` auth check + a way to put a contract in the call chain (the caller deploys one) |
| integer-overflow | `<0.8` pragma (or `unchecked` on `>=0.8`), no SafeMath on the path, a subtraction/addition that can wrap |
| weak-randomness | a `block.*`/readable-state source feeding the decision; the caller can read/compute the same value |
| selfdestruct | a `selfdestruct` reachable, OR a balance-predicate the force-feed satisfies; the contract deployable in a prior tx |
| uninitialized-proxy | a proxy/impl pattern + an `initialize` callable in the relevant context |
| front-running | an ordering-sensitive decision + a way to force the order (an atomic contract, or a mempool copy) |
| signature | an `ecrecover` check + a replayable/malleable/zero-address hash |
| accounting | a tracked balance/shares that a path can desync from real |
| visibility | a `private`/`internal` var used as a secret that `cast storage` reads |
| gas-griefing/DOS | a `for`-over-growing-set, a `transfer` to a caller-controlled partner, a check-then-act window |

## The universal precondition

The contract must have a **reachable transition** to the solved state — a
function the supplied caller (or a contract they deploy) can call whose
post-state satisfies `isSolved()`. If no such transition exists, the class is
falsified — `per-falsifier.md` / `negative-results.md`.

## The instance precondition

The exploit needs the LIVE per-instance values: the RPC URL, the private key,
the deployed contract addresses. Stale values from a dead instance fail — read
them fresh each time.

## The funding precondition

A `payable`-requiring exploit needs the supplied caller to have ether —
`cast balance $ME` checks; the deploy/attack carries `--value`.

## The tooling precondition

`cast`/`forge`/`solc` (or `web3`/`ethers`/`python`) present — `which cast forge
solc` confirms. A bytecode-only target needs `evm`/`heimdall`/`panoramix` to
decompile.
