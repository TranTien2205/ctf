# Payload map — the class → the payload shape → the verify

## The map

| Class | The payload | The verify |
|---|---|---|
| access-control | `cast send "setOwner(address)" $ME` | `cast call "owner()"` = caller |
| reentrancy | the `Reenter` contract + deposit+withdraw | `cast balance` → 0 |
| delegatecall | call proxy.fallback with the writer's selector | `cast storage` the slot |
| storage-collision | `cast send "setA(address)"` writes the wrong slot | `cast storage` the protected slot |
| tx.origin | the `Phish` contract + `attack(target)` | `cast call "owner()"` = caller |
| integer-overflow | `cast send "transfer(uint256)" 1` | `cast call "balances()"` → wrapped |
| weak-randomness | the `Predict` contract + `attack` | `cast call` the answer/`isSolved()` |
| selfdestruct | the funded `Force` + `boom(target)` | `cast balance`/`cast code` the target |
| uninitialized-proxy | `cast send "initialize(address)" $ME` | `cast call "owner()"` = caller |
| front-running | the `Sequencer` contract + `run` | the receipt's ordered logs |
| signature | `cast send "claim(bytes,uint256)"` the sig | the balance/flag change |
| accounting | the deposit/donate/withdraw sequence | `cast balance` the desync |
| visibility | `cast storage` the slot + `cast send` the gate | `cast call "locked()"` → false |
| gas-griefing | the refusing-partner / the loop-grow contract | `cast call` the bricked function reverts |
| constructor-EOA | the `Tricky` contract calling from its constructor | `cast call` the check-passed state |

## The payload-selection rule

The cheapest payload first:
- a bare `cast send` (no contract) before a contract
- a single contract before a multi-contract chain
- a same-tx atomic before a multi-tx sequence

The predicate + the primitive pick the payload family; the contract's specifics
pick the signature and args.

## The "the payload is a contract" note

Most web3 payloads are CONTRACTS, not strings — the exploit is a deployed
contract whose `run()`/`attack()`/`receive` does the work. The `cast send`
payloads are for the bare-setter / single-call cases only.
