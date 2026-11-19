# Per-mechanism map — the EVM primitive → the bug files

| Primitive | The bug classes | Files |
|---|---|---|
| `call` / `call{value}` | reentrancy, tx.origin context, the callback | `reentrancy.md`, `tx-origin.md` |
| `delegatecall` | storage-write, collision, uninit-lib, library-kill | `delegatecall.md`, `storage-collision.md`, `uninitialized-proxy.md` |
| `staticcall` | read-only-reentrancy, the snapshot oracle | `reentrancy-deep.md` |
| `selfdestruct` | force-feed, contract-deletion, library-kill | `selfdestruct.md` |
| `create`/`create2` | the lost-address, the constructor-EOA, the resurrect | `edge-cases.md`, `per-target.md` |
| `sstore`/`sload` | the predicate's slots, the collision, the private read | `storage-collision-deep.md`, `visibility.md` |
| `keccak256`/`sha3` | the signature/answer/commit — the hash binding | `signature-replay.md`, `weak-randomness.md` |
| `ecrecover` | the sig-replay/forgery | `signature-replay.md` |
| arithmetic `+ - * /` | overflow/underflow, the accounting desync | `integer-overflow.md`, `accounting-vault.md` |
| `block.*`/`tx.gasprice` | weak-randomness, front-running | `weak-randomness.md`, `front-running.md` |
| `for`/`while` loop | the unbounded-loop DOS | `gas-griefing-dos.md` |
| `revert`/`require` | the guard — what it protects, the refusing partner | `gas-griefing-dos.md`, `troubleshoot.md` |
| `msg.sender`/`tx.origin` | the caller model | `tx-origin.md`, `tx-origin-deep.md` |
| `extcodesize`/`codesize` | the EOA/constructor check | `edge-cases.md`, `tx-origin-deep.md` |
| `receive`/`fallback` | the ether/callback entry | `reentrancy.md`, `detection.md` |
| `payable` | the ether-accepting surface | `selfdestruct.md`, `edge-cases.md` |
| `modifier`/`onlyX` | the guard — the access check | `access-control.md`, `per-verb.md` |
| `private`/`internal` | the not-secret var | `visibility.md` |
| `unchecked` (0.8+) | the deliberate wrap | `integer-overflow-deep.md` |
| `super`/`inheritance` | the layout order (inherited vars take low slots) | `storage-collision-deep.md` |

## The entry-point map

| Entry | What it exposes |
|---|---|
| `receive()` | ether-only calls — the reentrancy hook |
| `fallback()` | unmatched calls — the delegatecall entry |
| a public function | the normal call surface |
| the constructor | the deploy-time state — the extcodesize-0 window |
| `init`/`initialize` | the post-deploy init — the uninit-proxy surface |
