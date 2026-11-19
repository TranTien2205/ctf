# Access-control map — the guard shapes indexed

## The guard-type → the bypass

| Guard type | The bypass | File |
|---|---|---|
| none — bare setter | call it | `access-control.md` |
| `onlyOwner`, owner uninitialized | `init`/`initialize` sets it | `uninitialized-proxy.md` |
| `onlyOwner`, owner settable | `setOwner`/`transferOwnership` unguarded | `access-control.md` |
| `require(msg.sender == tx.origin)` | constructor call (extcodesize 0) | `tx-origin-deep.md` |
| `require(tx.origin != msg.sender)` | a contract in the middle | `tx-origin.md` |
| `require(owner = tx.origin)` | a Phish forwards | `tx-origin.md` |
| `require(sig valid)` | replay/forge/zero-address | `signature-replay.md` |
| `require(x == privateVar)` | `cast storage` the var | `visibility.md` |
| `require(gasleft() ...)` | the gasleft gate — measure it | `edge-cases.md` |
| `require(!locked)` where `locked` settable | the unlock setter | `access-control.md` |
| a modifier on the wrong var | the guard protects a different slot | `access-control-deep.md` |
| `nonReentrant`/`locked` | a cross-function path the flag doesn't share | `reentrancy-deep.md` |

## The setter-type → the call

| Setter type | The call |
|---|---|
| `setOwner(address)` | `cast send "setOwner(address)" $ME` |
| `changeOwner(address)` | `cast send "changeOwner(address)" $ME` |
| `transferOwnership(address)` | `cast send "transferOwnership(address)" $ME` |
| `unlock(bytes32)`/`unlock()` | `cast send "unlock(...)"` |
| `setFlag(bool)`/`setSolved()` | `cast send "setFlag(bool)" true` |
| `initialize(address)`/`init(...)` | `cast send "initialize(address)" $ME` |
| a `fallback` that sets owner | `cast send $CH ""` / a raw call |
| a `register`/`join` that grants | `cast send "register()"` |

## The "where the guard reads" map

| The guard reads | The bypass |
|---|---|
| `msg.sender` | the caller — or a contract in the middle changes it |
| `tx.origin` | the origin — a Phish, or a constructor's codesize-0 |
| a storage var | is the var settable? `cast storage` it |
| a signature | `signature-replay.md` — replay/forge |
| a `private` var | `cast storage` reads it — `visibility.md` |
| `address(this)`/`extcodesize` | a constructor's codesize-0 |
| `block.*` | the time/block source — public |

## The "the guard isn't there" case

The most common web3 bug: NO guard at all. A `public` function that writes
`owner`/`locked`/`flag` and anyone can call it — the reachability enumeration
finds it. `access-control.md` + `access-control-deep.md` are the whole class.
