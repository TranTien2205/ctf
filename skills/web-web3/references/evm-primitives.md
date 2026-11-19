# EVM primitives — call / delegatecall / staticcall / selfdestruct / CREATE

The exploit classes all reduce to a handful of EVM primitives. Name the
primitive the challenge misuses, and the exploit shape follows.

## call — a foreign call in the callee's context

```solidity
target.call{value: v}(data)   → target's code runs, target's storage, target's msg.sender is THIS contract
```

- `msg.sender` inside `target` = the calling contract, not `tx.origin`
- reentrancy: `call` forwards gas; the callee's `fallback`/`receive` runs and can call back in
- a `call` to an attacker-controlled address runs attacker code

## delegatecall — foreign code in the CALLER's context

```solidity
target.delegatecall(data)     → target's code runs, THIS contract's storage, THIS contract's msg.sender
```

- the dangerous one: `target`'s code writes THIS contract's storage by slot
- `msg.sender` and `msg.value` are PRESERVED — the callee sees the original caller
- a `delegatecall` to an attacker-controlled address = full storage control → own the contract
- the library/`WalletLibrary` shape: a `delegatecall` into shared code that can `selfdestruct` or `init`

## staticcall — a read-only foreign call

```solidity
target.staticcall(data)       → target's code runs, cannot write state
```

- a reentrancy guard that uses `staticcall` for the check reads a snapshot
- a `staticcall` cannot `selfdestruct`, write storage, or emit — but it can read

## selfdestruct — destroy the contract, force-send its balance

```solidity
selfdestruct(payable dest)    → this contract's code+storage erased, its ether FORCED to dest
```

- **force-feeding**: `selfdestruct(attacker)` sends ether to `attacker` even when it has no `receive`/`fallback` — the classic "contract that rejects ether" bypass
- a `selfdestruct` in a `delegatecall`ed library destroys the CALLER (the parity wallet bug)
- deprecated post-Cancun for same-tx creation, but the force-send still works for pre-existing contracts

## CREATE / CREATE2 — deploy a contract

```solidity
new C{salt: s}()              → CREATE2: address = f(deployer, salt, initcode) — PREDICTABLE
```

- CREATE2 address is deterministic — pre-compute where a contract will deploy
- a contract's address exists before its code (CREATE2) — "call an address with no code yet"
- the "no code = no callback" check defeated: deploy to a known CREATE2 address, call, then the code lands
- a contract under construction has `extcodesize == 0` — the `extcodesize == 0 → "is an EOA"` check is bypassed by calling from a constructor

## The storage model

```solidity
slot 0: owner / first declared var
slot N: the Nth declared var; packed smaller-than-32B vars share a slot
mapping(k => v): stored at keccak256(k . slot) — the slot isn't enumerable
dynamic array: length at slot, data at keccak256(slot) + i
```

- **storage collision**: two contracts in a delegatecall layout must declare vars in the same order — a mismatch overwrites the wrong slot (e.g. a `lib` address slot overwritten with an attacker address)
- a private var is NOT secret — `eth_getStorageAt(addr, slot)` reads any slot
- a `delegatecall` target writes YOUR storage at ITS declared slots

## The gas / value semantics

- `msg.value` — ether sent with the call; a `payable` function can require/refuse it
- `.transfer`/`.send` — 2300 gas, no reentrancy room (but a `selfdestruct` force-send ignores it)
- `call{value:}` — all remaining gas → reentrancy room
- `tx.gasprice`, `block.timestamp`, `block.number`, `blockhash` — the weak-randomness / front-running surface

## The caller model

- `msg.sender` — the IMMEDIATE caller (a contract or an EOA)
- `tx.origin` — the EOA that STARTED the transaction — `require(tx.origin == msg.sender)` is a phishing invite: a contract the victim calls makes the check pass differently
- `address(this)` — the contract itself; `address(this).balance` its ether
- an EOA has no code; a contract has `extcodesize > 0` — but `extcodesize == 0` is ALSO true inside a constructor (the "contract that looks like an EOA" trap)
