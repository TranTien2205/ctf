# Detection index — the full signal table

## Predicate-shape signals (read `isSolved()` first)

| Predicate | Class | File |
|---|---|---|
| `owner() == X` | access-control / tx.origin | `access-control.md`, `tx-origin.md` |
| `balance == 0` / `> K` | reentrancy / selfdestruct / drain | `reentrancy.md`, `selfdestruct.md` |
| `flag`/`solved`/`locked` flip | access-control / visibility | `access-control.md`, `visibility.md` |
| `count >= N` | reentrancy / a callable-increment | `reentrancy.md` |
| `winner == X` | front-running / randomness | `front-running.md`, `weak-randomness.md` |
| `code.length == 0` | selfdestruct / constructor | `selfdestruct.md`, `edge-cases.md` |
| `answer == X` | weak-randomness / visibility | `weak-randomness.md` |

## Source-keyword signals

| Keyword | Class |
|---|---|
| `delegatecall` | delegatecall / storage-collision |
| `tx.origin` | tx.origin |
| `call{value:` then `-=` | reentrancy |
| `pragma ^0.4-^0.7` | integer-overflow |
| `unchecked` | integer-overflow (0.8+) |
| `selfdestruct` | selfdestruct |
| `block.timestamp`/`blockhash`/`prevrandao` | weak-randomness |
| `private`/`internal` as a secret | visibility |
| `ecrecover`/`ECDSA.recover` | signature |
| `initialize`/`init`/`initializer` | uninitialized-proxy |
| `extcodesize`/`codesize` | constructor-EOA |
| `deposit`/`withdraw`/`shares`/`rate` | accounting-vault |
| `winner`/`claim`/`auction` | front-running |
| `flash`/`borrow`/`flashLoan` | flashloan-oracle |
| `for`/`while` over a growing array | gas-griefing-dos |
| `transfer`/`transferFrom`/`balanceOf` | token-standards |
| a bare `setOwner`/`unlock`/`setFlag` | access-control |

## Bytecode-op signals

| Opcode | Class |
|---|---|
| `DELEGATECALL` | delegatecall |
| `ORIGIN` | tx.origin |
| `CALL` + `SSTORE` after | reentrancy |
| `SELFDESTRUCT` | selfdestruct |
| `TIMESTAMP`/`BLOCKHASH`/`DIFFICULTY`/`NUMBER`/`COINBASE` | weak-randomness |
| `CODESIZE`/`EXTCODESIZE` | the constructor-EOA check |
| `ECRECOVER` (precompile 0x01) | signature |
| `CREATE`/`CREATE2` | the deploy/address bugs |
| `SSTORE` to a predicate slot | the reachable transition |

## The package signals

| Signal | The read |
|---|---|
| `Setup.sol` + `isSolved()` | the predicate-driven shape — `detection.md` |
| an RPC URL + private key | the live private chain |
| `foundry`/`hardhat`/`truffle` config | the toolchain |
| a single `.sol` + no setup | the contract IS the challenge — read its state |
