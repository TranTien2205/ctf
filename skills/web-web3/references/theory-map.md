# Theory map — the root-cause → the bug classes it produces

## The limits

| The contract can't | The bug classes |
|---|---|
| hide its state | visibility, storage-collision, weak-randomness (the readable secret) |
| tell the real caller | tx.origin, the constructor-EOA, signature (the wrong binding) |
| control the callback | reentrancy, read-only-reentrancy, the token-hook |
| trust a delegatecall | delegatecall, storage-collision, uninitialized-proxy, the lib-kill |
| get real entropy | weak-randomness, front-running (the ordering) |
| take back a tx | every exploit is permanent — the attributable-send model |
| check its arithmetic | integer-overflow, accounting (the desync) |
| refuse the ether | selfdestruct force-feed |
| distinguish its contexts | uninitialized-proxy (proxy vs impl storage) |
| keep two numbers synced | accounting-vault, the share-price, the flash-loan |

## The mechanism → the class

| EVM mechanism | The class it enables |
|---|---|
| `call` | reentrancy |
| `delegatecall` | delegatecall/collision/kill |
| `staticcall` | read-only-reentrancy |
| `selfdestruct` | selfdestruct family |
| `create`/`create2` | the address/constructor/resurrect |
| `tx.origin`/`msg.sender` | the origin/sender confusion |
| `block.*` | weak-randomness/front-running |
| `sstore`/`sload` | the collision, the readable secret |
| `ecrecover` | the signature family |
| `+ - *` | the overflow/accounting |
| `extcodesize`/`codesize` | the EOA/constructor check |

## The "the predicate is the root" note

`isSolved()` IS the specification of the exploit — it names which state limit
the challenge exercises. An `owner()` predicate is the caller-identity limit; a
`balance` predicate is the state/callback limit; a `flag` predicate is the
write-access limit. The theory explains the class; the predicate selects it.
