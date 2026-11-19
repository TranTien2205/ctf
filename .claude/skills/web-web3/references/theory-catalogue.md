# Theory catalogue — why each bug class exists

## access-control — the contract can't read the developer's intent

The code does exactly what it says — a `public` function is callable, a `private`
one isn't, an `internal`-intended function left `public` is public. The bug is
the gap between "the author meant this to be owner-only" and "the code allows
anyone" — `access-control.md`.

## reentrancy — the contract can't control the callback

`call` forwards gas and runs arbitrary code — the callee's `receive`/`fallback`
is attacker code that calls back in. The contract assumed the `call` returned
control; it doesn't — `reentrancy.md`.

## delegatecall — the contract can't tell whose storage

`delegatecall` runs foreign code on YOUR storage — the caller can't tell the
code is writing ITS slots by position. The storage-model abstraction leaks —
`delegatecall.md`, `storage-collision.md`.

## tx.origin — the contract can't tell the real caller

`tx.origin` is the EOA that started the tx — a contract in the middle makes
`msg.sender` the contract while `tx.origin` stays the EOA. The caller model has
two fields and the contract uses the wrong one — `tx-origin.md`.

## integer-overflow — the contract can't trust its math

Pre-0.8, `0 - 1` wraps to `2**256-1` — the EVM's arithmetic is modular, not
checked. The `require` on a wrapped expression passes — `integer-overflow.md`.

## weak-randomness — the contract can't get real entropy

`block.*` is public per-block — a contract that reads it for a "random" or a
"secret" is reproducible. The chain has no private entropy — `weak-randomness.md`.

## visibility — the contract can't hide its storage

`private` hides a var from OTHER CONTRACTS, not from `eth_getStorageAt` —
the ledger is public. The "secret" was never secret — `visibility.md`.

## selfdestruct — the contract can't refuse the ether

`selfdestruct`'s force-send runs no code on the target — a contract can't
reject it. The "unpayable" invariant is a lie — `selfdestruct.md`.

## uninitialized-proxy — the contract can't distinguish its contexts

The proxy and the impl have SEPARATE storage — an `init` meant for the proxy's
context is callable on the impl's (and vice-versa) — `uninitialized-proxy.md`.

## signature — the contract can't bind the sig to its intent

`ecrecover` recovers the signer of the EXACT hash — a hash missing a nonce/
chainid/sender/domain is replayable. The binding is in the hash, not the sig —
`signature-replay.md`.

## accounting — the contract can't keep two numbers in sync

The tracked `shares`/`totalAssets` and the real `balance` desync on a path the
author didn't update — a donation, a reentrancy, a rounding —
`accounting-vault.md`.

## the shared root

Every class is a trust the contract extends that doesn't exist — a hidden state,
a known caller, a controlled callback, private entropy, a single storage, a
bound sig, a synced accounting.
