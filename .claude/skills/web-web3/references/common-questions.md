# Common questions — the things that come up

## "isSolved() returned true before I did anything — did I solve it?"

No — the predicate was already true, or the setup is different than assumed.
Re-read the `Setup.sol` — the predicate may read a different contract, or the
challenge expects a different solved state. The solve is a `false → true`
transition attributable to the caller.

## "the transaction mined but isSolved() is still false — what happened?"

The tx succeeded but didn't change the predicate's state — the wrong transition.
Re-read the predicate and the reachable-call inventory; the sent call touched
a different slot than `isSolved()` reads.

## "cast call says it works but cast send reverts"

The dry-run's fork/sim state differed from the live chain — a nonce, a block
value, a state assumption. For a block-dependent exploit (weak-randomness),
compute the value at SEND-time, not read-then-send — the block changes between.

## "the contract rejects my ether — is the balance-check predicate unsolvable?"

No — `selfdestruct` force-feeds ether to a contract that rejects `call{value}`.
Deploy a funded contract and `selfdestruct` into the target — `selfdestruct.md`.

## "the function is onlyOwner — is the class closed?"

Not necessarily — is `owner` settable (`setOwner`/`init`/`transferOwnership`
unguarded)? Is the guard `tx.origin`-based (phishable)? Does a `delegatecall`
let you write the `owner` slot? The guard's bypass is the bug —
`access-control-map.md`.

## "the source doesn't match the bytecode — which do I trust?"

The bytecode — `cast code` + `evm disasm`/`heimdall`/`panoramix`. The shipped
`.sol` is a decoy; the deployed code is the real surface.

## "a private variable looks important — can I read it?"

Yes — `cast storage $CH <slot>` reads any slot. `private` only hides a var from
other contracts, not from `eth_getStorageAt`. `visibility.md`.

## "the reentrancy doesn't re-enter — what's wrong?"

The call is `.transfer`/`.send` (2300 gas — no room) or a `nonReentrant` guard.
Check the call type and the guard — `reentrancy-deep.md`. If both hold, the
class is falsified — a different drain (accounting, force-feed).

## "there's no obvious vulnerability — where do I look?"

Enumerate the reachable non-view functions; for each, does it write the
predicate's slot? The unguarded setter is the intended solve more often than a
deep bug. If none writes the slot, the predicate's state is unreachable — the
challenge's path is a different contract the setup deploys.
