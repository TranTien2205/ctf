# Mechanism index — every EVM mechanism and the bug it enables

## The execution mechanisms

| Mechanism | The file | The bug |
|---|---|---|
| the transaction / the call-frame | `mechanism.md`, `mechanism-deep.md` | the whole model |
| `call` / `call{value}` | `evm-primitives.md`, `reentrancy.md` | the callback / reentrancy |
| `delegatecall` | `delegatecall.md`, `delegatecall-deep.md` | storage-write / collision / lib-kill |
| `staticcall` | `evm-primitives.md`, `reentrancy-deep.md` | the snapshot read |
| `selfdestruct` | `selfdestruct.md`, `selfdestruct-deep.md` | force-feed / delete / kill |
| `create`/`create2` | `evm-primitives.md`, `edge-cases.md` | the address / the resurrect |
| `callcode` | `evm-primitives.md` | legacy delegatecall |

## The context mechanisms

| Mechanism | The file | The bug |
|---|---|---|
| `msg.sender` | `evm-primitives.md`, `tx-origin.md` | the caller model |
| `tx.origin` | `tx-origin.md`, `tx-origin-deep.md` | the phish / the EOA check |
| `msg.value`/`payable` | `evm-primitives.md`, `selfdestruct.md` | the ether surface |
| `address(this)` | `evm-primitives.md` | the storage context |
| `extcodesize`/`codesize` | `edge-cases.md`, `tx-origin-deep.md` | the EOA/constructor check |

## The storage mechanisms

| Mechanism | The file | The bug |
|---|---|---|
| the slot layout | `storage-collision-deep.md`, `evm-primitives.md` | the collision |
| `private`/`internal` | `visibility.md` | the readable "secret" |
| the mapping/array hash | `storage-collision-deep.md` | the hashed-slot read |
| the packed vars | `storage-collision-deep.md` | the packed clobber |
| inheritance layout | `storage-collision-deep.md` | the inherited-slot order |

## The arithmetic mechanisms

| Mechanism | The file | The bug |
|---|---|---|
| the wrap (`<0.8`) | `integer-overflow.md`, `integer-overflow-deep.md` | underflow/overflow |
| `unchecked` (0.8+) | `integer-overflow-deep.md` | the deliberate wrap |
| `SafeMath` | `integer-overflow.md` | the guard — its absence on a path |
| the accounting invariant | `accounting-vault.md`, `accounting-vault-deep.md` | the desync |

## The block/randomness mechanisms

| Mechanism | The file | The bug |
|---|---|---|
| `block.timestamp`/`number`/`blockhash`/`prevrandao`/`coinbase`/`difficulty`/`basefee` | `weak-randomness.md`, `weak-randomness-deep.md` | the predictable source |
| `tx.gasprice`/the mempool | `front-running.md`, `front-running-deep.md` | the ordering |
| `gasleft()` | `edge-cases.md`, `gas-griefing-dos.md` | the gas gate |

## The signature mechanism

| Mechanism | The file | The bug |
|---|---|
| `ecrecover`/the precompiles | `signature-replay.md`, `signature-replay-deep.md` | replay/forge/zero-addr/malleability |
| EIP-712/`personal_sign` | `signature-replay-deep.md` | the domain-binding |
| `keccak256`/`abi.encodePacked` | `signature-replay-deep.md`, `edge-cases.md` | the hash-collision |
