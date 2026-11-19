# Edge cases — the cases that don't fit the clean table

## The boundary cases

| Case | The reality |
|---|---|
| the contract rejects ALL ether | `selfdestruct` force-feeds it — no receive needed |
| `.transfer` (2300 gas) blocks reentrancy | a `selfdestruct` or a cross-function path still works |
| `extcodesize == 0` means "EOA" | a contract in its CONSTRUCTOR has code-size 0 — call from the constructor |
| a `private` var looks safe | `cast storage` reads it — private ≠ secret |
| `blockhash(block.number)` | always `0` — the contract computes on 0 |
| `blockhash(n)` too old | returns `0` for `n` > 256 blocks back — the "random" is 0 |
| a `staticcall` reentrancy guard | reads a snapshot — the real state changed mid-tx |
| CREATE2 to a selfdestructed address | code returns to a "deleted" address |
| `tx.origin == msg.sender` "EOA check" | a contract in its constructor is `extcodesize == 0` |
| a payable function with `msg.value == 0` | the guard reads the wrong field |
| `delegatecall` preserving `msg.sender` | the callee sees the ORIGINAL caller — auth passes unexpectedly |
| a mapping's "hidden" value | `keccak256(key . slot)` — `cast index` computes it |
| a dynamic array's element | `keccak256(slot) + i` — read each element |
| a packed struct | consecutive small vars share a slot — read the whole slot, split by width |

## The EVM-quirk cases

| Quirk | The exploit angle |
|---|---|
| a contract under construction | `extcodesize == 0` → passes EOA checks |
| `selfdestruct` to a contract that selfdestructs | the second `selfdestruct`'s ether goes to the first's target |
| a `receive` that reverts | can't stop a `selfdestruct` force-feed |
| `msg.sig`/`msg.data` in a fallback | the fallback's calldata is attacker bytes — route it |
| a `payable` fallback that reverts | can't stop ether via selfdestruct/coinbase |
| `block.coinbase`/`difficulty`/`prevrandao` | the validator/beacon values — public per block |
| a `delegatecall` to a contract that selfdestructs | destroys the CALLER |
| `abi.encodePacked` hash collisions | `encodePacked(a, b)` collides when a/b are dynamic — two different pairs hash the same |

## The simulation/live split

- `cast call` (eth_call) simulates — state UNCHANGED on-chain
- `forge test` forks — local only
- a `cast send` is the only thing that flips the live predicate

A "solved" on the fork that the live `isSolved()` doesn't confirm is not a solve —
the live chain is the ground truth.

## The instance-scoping trap

The RPC URL, the private key, and the contract addresses are PER-INSTANCE. A
solve script hardcoded to a dead instance fails on the new one — always read the
addresses from the challenge's live setup, never reuse across instances.
