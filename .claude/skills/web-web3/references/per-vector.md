# Per-vector map — the exploit vector → the file

## The call-path vectors

| Vector | The file |
|---|---|
| an external `call`/`call{value}` to attacker code | `reentrancy.md` |
| a `delegatecall` to a controlled/mismatched target | `delegatecall.md`, `storage-collision.md` |
| a `staticcall`-read mid-state | `reentrancy-deep.md` |
| a `selfdestruct` | `selfdestruct.md` |
| a `create`/`create2` | `edge-cases.md`, `per-target.md` |
| a callback/`receive`/`fallback` | `reentrancy.md`, `token-standards.md` |
| a token hook (`tokensReceived`/`onERC*`) | `token-standards.md` |

## The auth vectors

| Vector | The file |
|---|---|
| `msg.sender` auth | `access-control.md` |
| `tx.origin` auth | `tx-origin.md`, `tx-origin-deep.md` |
| `ecrecover`/signature auth | `signature-replay.md`, `signature-replay-deep.md` |
| `extcodesize`/`codesize` EOA check | `edge-cases.md`, `tx-origin-deep.md` |
| a `private`-var gate | `visibility.md` |

## The state vectors

| Vector | The file |
|---|---|
| a bare setter | `access-control.md` |
| an `initialize`/`init` | `uninitialized-proxy.md` |
| a storage-collision write | `storage-collision.md` |
| a `private`-var read | `visibility.md` |
| a balance/tracked-value desync | `accounting-vault.md` |
| an arithmetic wrap | `integer-overflow.md` |

## The decision vectors

| Vector | The file |
|---|---|
| `block.*`-fed decision | `weak-randomness.md` |
| a first-come/ordering decision | `front-running.md` |
| a price/oracle decision | `flashloan-oracle.md` |
| a balance-read decision | `flashloan-oracle.md`, `accounting-vault.md` |

## The destruction vectors

| Vector | The file |
|---|---|
| `selfdestruct` force-feed | `selfdestruct.md` |
| `selfdestruct` code-delete | `selfdestruct-deep.md` |
| a library `selfdestruct` via delegatecall | `delegatecall-deep.md`, `uninitialized-proxy-deep.md` |
| a refusing partner / a loop | `gas-griefing-dos.md` |

## The multi-step vectors

| Vector | The file |
|---|---|
| the atomic sequencer | `front-running.md`, `exploitation.md` |
| the deploy-then-call chain | `multi-step-chains.md` |
| the init-then-kill | `uninitialized-proxy-deep.md` |
| the collision-then-delegate | `storage-collision-deep.md` |
