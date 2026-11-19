# Per-bug catalogue — every bug class fully indexed

## The complete class list

| # | Class | The file | The first call |
|---|---|---|---|
| 1 | access-control | `access-control.md` | `cast send "setOwner"` |
| 2 | reentrancy | `reentrancy.md` | the `Reenter` contract |
| 3 | delegatecall | `delegatecall.md` | call through the proxy |
| 4 | storage-collision | `storage-collision.md` | `cast send "setA"` |
| 5 | tx.origin | `tx-origin.md` | the `Phish` contract |
| 6 | integer-overflow | `integer-overflow.md` | `cast send` the wrap |
| 7 | weak-randomness | `weak-randomness.md` | the `Predict` contract |
| 8 | selfdestruct | `selfdestruct.md` | the funded `Force` + `boom` |
| 9 | uninitialized-proxy | `uninitialized-proxy.md` | `cast send "initialize"` |
| 10 | front-running | `front-running.md` | the `Sequencer` contract |
| 11 | signature | `signature-replay.md` | `cast send` the sig |
| 12 | accounting | `accounting-vault.md` | the desync sequence |
| 13 | visibility | `visibility.md` | `cast storage` the slot |
| 14 | gas-griefing/DOS | `gas-griefing-dos.md` | the refusing partner / the loop |
| 15 | token-standards | `token-standards.md` | the token's surface |
| 16 | flashloan-oracle | `flashloan-oracle.md` | the atomic skew |

## The class → the mechanism → the predicate

| Class | The mechanism | The predicate it flips |
|---|---|---|
| access-control | an unguarded write | `owner`/`flag`/`locked` |
| reentrancy | `call`-then-update | `balance`/`count` |
| delegatecall | foreign code on caller storage | `owner`/a slot |
| storage-collision | a delegatecall slot mismatch | `owner`/the predicate slot |
| tx.origin | origin vs sender | `owner` |
| integer-overflow | the wrap | `balances`/`count` |
| weak-randomness | a predictable source | `answer`/`winner` |
| selfdestruct | force-feed / delete | `balance`/`code.length` |
| uninitialized-proxy | a callable init | `owner` |
| front-running | the ordering | `winner`/`first` |
| signature | a replayable sig | `verified`/`signer` |
| accounting | a desync | `rate`/`shares`/`balance` |
| visibility | a readable secret | a `private`-gated flag |
| gas-griefing | the DOS | the operational check |
| token-standards | the ERC surface | a token state |
| flashloan-oracle | the atomic skew | `price`/`rate`/`balance` |

## The "check first" per class

| Class | The cheapest check |
|---|---|
| access-control | `cast call` the getter — is `owner` a bare setter's target? |
| reentrancy | the call type — `.transfer`/`call`? |
| delegatecall | `cast storage` the impl slot + the layouts |
| tx.origin | `grep tx.origin` — the check's form |
| integer-overflow | `grep pragma` — `<0.8`? `unchecked`? |
| weak-randomness | `grep block.` — the source? |
| selfdestruct | `grep selfdestruct` — reachable? a balance predicate? |
| the rest | the per-bug file's detection fingerprint |
