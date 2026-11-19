# Detection map — a signal → the class → the file

## Source-level signals

| Signal | Class | File |
|---|---|---|
| `delegatecall` | delegatecall / storage-collision | `delegatecall.md` |
| `tx.origin` | tx.origin | `tx-origin.md` |
| `call{value:}` then a `-=`/`write` | reentrancy | `reentrancy.md` |
| `pragma ^0.4-^0.7`, no SafeMath | integer-overflow | `integer-overflow.md` |
| `unchecked {` | integer-overflow | `integer-overflow.md` |
| `selfdestruct` | selfdestruct / force-feed / kill | `selfdestruct.md` |
| `block.timestamp`/`blockhash`/`prevrandao` | weak-randomness | `weak-randomness.md` |
| `private`/`internal` used as a secret | visibility | `visibility.md` |
| `ecrecover`/`ECDSA.recover` | signature | `signature-replay.md` |
| `initialize`/`init`/`initializer` | uninitialized-proxy | `uninitialized-proxy.md` |
| `extcodesize`/`codesize` EOA check | constructor trick | `edge-cases.md` |
| `deposit`/`withdraw`/`shares`/`rate` | accounting-vault | `accounting-vault.md` |
| `winner`/`claim`/`auction` | front-running | `front-running.md` |
| a `public` setter with no guard | access-control | `access-control.md` |
| a `fallback`/`receive` | the entry point — check what's callable | `detection.md` |

## Bytecode-level signals (no source)

| Signal | Class |
|---|---|
| a `DELEGATECALL` op | delegatecall — read the target slot |
| `SSTORE` to a slot the predicate reads | the writer — the reachable transition |
| `SELFDESTRUCT` op | selfdestruct path |
| `CALL` with value then `SSTORE` | reentrancy candidate |
| `ORIGIN` op | tx.origin check |
| `TIMESTAMP`/`BLOCKHASH`/`NUMBER`/`DIFFICULTY` | weak-randomness |
| `CODESIZE`/`EXTCODESIZE` check | the EOA/constructor trick |
| `ECRECOVER` precompile call | signature |

## The predicate-side signal

`isSolved()`'s expression is the FIRST signal — `attack-shapes.md` maps the
predicate shape to the class. Read it before the contract body; it aims the
detection.

## The order

`isSolved()` → the reachable-call inventory → the source signals → the bytecode
confirmation. The predicate narrows to a class; the reachable functions confirm
a transition exists; the source/bytecode signals name which one.
