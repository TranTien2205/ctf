# Per-mechanism (deep) — each primitive's exploit surface in full

## `call` / `call{value}` — the foreign call

- forwards gas (all remaining, or `call{gas:}` a subset) + `value`
- runs the callee's code — `msg.sender` = the caller, `this` = callee
- a `call` to attacker code runs `receive`/`fallback` → reentrancy
- a `call` to a contract-that-reverts → the `success` bool / the revert
- the bug: the `call` is before the state update, OR the callee is attacker-
  controlled and the contract depends on its behavior

## `delegatecall` — foreign code on your storage

- runs `target`'s code; `address(this)`/`msg.sender`/`msg.value` = the CALLER's
- `SSTORE N` in the target's code writes the CALLER's slot N
- the bug: the target is influenceable (a param/a settable var), OR the
  caller/callee layouts mismatch → the collision
- the deepest bug — a `delegatecall` is total storage control if the target is
  attacker code

## `staticcall` — the read-only call

- the callee can't `SSTORE`/`selfdestruct`/emit — a snapshot read
- the bug: a `staticcall`-checked guard reads a mid-state that a reentrancy
  already changed — the read-only-reentrancy oracle

## `selfdestruct` — the destroy-and-send

- erases code+storage, sends ALL ether to the beneficiary, no code on the target
- the bug: force-feed a refusing contract; delete the code; the library-kill
  (delegatecall'd selfdestruct destroys the caller)
- post-Cancun: full delete only for same-tx-created contracts

## `create` / `create2` — the deploy

- CREATE's address = `keccak256(deployer, nonce)[12:]` — `cast getAddress`
- CREATE2's address = `keccak256(0xff . deployer . salt . keccak256(initcode))[12:]`
  — deterministic and re-deployable
- the bug: the predictable address, the constructor-EOA trick, the resurrect

## The context ops — `msg.sender`/`tx.origin`/`msg.value`/`block.*`

- `tx.origin` the EOA root; `msg.sender` the immediate caller — the phish split
- `block.timestamp`/`number`/`blockhash`/`prevrandao`/`coinbase`/`difficulty`/
  `basefee`/`gaslimit` — all public per-block — the weak-randomness surface
- `gasleft()`/`tx.gasprice` — the gas gate, the ordering

## The precompiles

- `ecrecover` (0x01) — the sig check — `address(0)` on bad input
- `sha256`/`ripemd160`/`identity`/`modexp` — the crypto helpers
- `ecadd`/`ecmul`/`ecpairing` — the ZK surface
- `blake2f` — the hash

## The arithmetic

- `add`/`sub`/`mul`/`div`/`mod`/`addmod`/`mulmod`/`exp`/`signextend`
- pre-0.8 wrap; `>=0.8` revert; `unchecked` re-open; `div`-by-0 reverts
- the bug: the wrap and the accounting-desync

## The storage ops

- `SSTORE`/`SLOAD` — the slot write/read — the predicate's slots, the collision,
  the `private`-read
- `TSTORE`/`TLOAD` (transient, Cancun+) — per-tx scratch — a reentrancy flag
  that survives the call's return only for the tx

## The environmental ops

- `ADDRESS`, `BALANCE`, `SELFBALANCE`, `CALLER`, `CALLVALUE`, `CALLDATA*`,
  `CODESIZE`, `EXTCODESIZE`, `RETURNDATA*`, `PC`, `MSIZE`, `GAS` — the reads
  the exploit reasons about
