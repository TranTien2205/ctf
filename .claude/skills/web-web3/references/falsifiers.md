# Falsifiers — the observations that close a web3 path

## The class falsifier

> **The solved predicate depends on state no external caller can change.**

The contract is solved-by-construction unreachable: the predicate reads a var
no function writes, a state only the constructor set, or a balance only a
selfdestruct the contract never calls could move. If every reachable transition
is enumerated and none touches the predicate's slots, the class is closed — the
exploit needs a different contract/bug, not a sixth payload.

## Per-path falsifiers

| Path | Falsifier |
|---|---|
| unprotected setter | the setter is `onlyOwner`/`internal`/nonexistent — no reachable call writes the predicate's slot |
| `tx.origin` phish | the check is `msg.sender`-based, or no intermediate contract can be placed in the call chain |
| reentrancy | the function uses `.transfer` (2300 gas), a reentrancy guard, or updates state before the external call (checks-effects-interactions) |
| delegatecall storage | no `delegatecall` exists, or its target is hardcoded and storage layout is safe |
| integer wrap | the compiler is `>=0.8` (built-in over/underflow checks revert) and no `unchecked` block wraps the path |
| weak randomness | the contract doesn't read `block.timestamp`/`blockhash`/etc. for the decision |
| selfdestruct force-feed | the predicate isn't a balance check, or the contract already accepts ether |
| uninitialized proxy | the implementation's `initialize` is `initializer`-protected or already init'd |
| storage collision | the proxy/impl layouts match — no slot mismatch |
| front-running | the decision isn't ordering-sensitive, or a commit-reveal already protects it |
| signature replay | the signature includes a nonce/chain-id/expiry, or `ecrecover` isn't used |

## The "no reachable transition" test

Enumerate the contract's external/public non-view functions. For each, ask:
does it write a slot `isSolved()` reads? If the predicate reads slot N and no
reachable function writes slot N (directly, via delegatecall, or via a selfdestruct
force-send), the path is falsified.

## The simulation falsifier

`cast call`/`forge` the exact exploit: if the simulated `isSolved()` stays
`false`, the exploit logic is wrong — fix the transition before spending a real
transaction. A simulation that passes but a live tx that reverts points at gas,
nonce, or a state assumption that changed.

## The budget falsifier

Three transactions reverted on the same transition with no new revert reason →
the path is stuck. `decide.py escalate`: a wrong bug-class guess is the common
cause — re-read the predicate and the reachable-call inventory.
