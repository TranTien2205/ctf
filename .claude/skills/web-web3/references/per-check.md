# Per-check map — the `require`/`assert` → the bypass

## The require-shape inventory

| The `require` | The bypass |
|---|---|
| `require(msg.sender == owner)` | own the contract, or a contract-in-middle changes `msg.sender` |
| `require(tx.origin == ...)` | `tx-origin.md` — the origin is a fixed EOA, a phish-able value |
| `require(tx.origin != msg.sender)` | `tx-origin.md` — a contract in the middle |
| `require(msg.sender == tx.origin)` | `tx-origin-deep.md` — a constructor's `extcodesize==0` |
| `require(balances[me] >= x)` | integer-overflow / reentrancy — the balance lies |
| `require(!locked)` | an unlock setter, or `locked` is a settable var |
| `require(block.number > N)` | wait — or a block the predicate accepts |
| `require(x == secret)` where secret is `private` | `cast storage` the secret — `visibility.md` |
| `require(ecrecover(...) == signer)` | `signature-replay.md` — replay/forge/zero-addr |
| `require(initialized)`/`require(!initialized)` | `uninitialized-proxy.md` — the flag context |
| `require(amount <= limit)` | integer-overflow — wrap `amount` past the check |
| `require(caller.code.length == 0)` | `edge-cases.md` — a constructor call |
| `require(success)` on a `call` | the callee must not revert — a benign call for the check |

## The assert / revert shapes

| The shape | The note |
|---|---|
| `assert` | an invariant — a violation = a bug in the contract's own math |
| `revert`/`if(!...) revert` | the explicit guard — trace which one fires |
| a `modifier`'s `require` | the guard is the modifier — find what it checks |

## The "the require is the bug" case

Some `require`s ARE the vulnerability — a `require` on a wrapped expression
(`require(0 - 1 >= 0)` passes), a `require` that reads `tx.origin`, a `require`
that a `delegatecall` bypasses. The guard's EXPRESSION is the surface.

## The require-trace read

`cast run <txhash>`/`forge -vvvv` traces the execution — the failing `require`'s
location and the values it compared. The trace names the unmet precondition;
the bypass is whatever state the `require` actually checks.
