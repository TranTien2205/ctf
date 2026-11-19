# Detection (deep) — the bytecode and source signals

## The dispatch-table read

Every contract's runtime bytecode starts with a dispatcher — it compares
`calldataload(0)`'s first 4 bytes (the selector) against each function's
`keccak256(sig)[0:4]` and `jump`s. Reading the dispatch table enumerates the
reachable functions without the ABI:

```bash
cast code $CH --rpc-url $RPC | evm disasm | grep -E "PUSH4|EQ|JUMPI"
# each PUSH4 <selector> is a reachable function
```

`cast 4byte <selector>` resolves the selector to a signature guess.

## The SSTORE map

`evm disasm` + grep `SSTORE` finds every state write — the slots the code
touches. The slot that `isSolved()` reads (via the predicate's `SLOAD` chain)
cross-referenced with the functions that `SSTORE` it = the candidate transitions.

```
SSTORE slot N  →  the function writes slot N
SLOAD slot N   →  the function reads slot N
```

A `private`/`internal` marking doesn't appear in bytecode — the slots are all
just numbers; the read reveals the real data flow.

## The context-op signals

| Opcode | What it reads | The class it signals |
|---|---|---|
| `ORIGIN` | `tx.origin` | tx.origin — auth on origin |
| `CALLER` | `msg.sender` | the normal caller check |
| `CALLVALUE` | `msg.value` | a payable/ether path |
| `TIMESTAMP`,`NUMBER`,`BLOCKHASH`,`DIFFICULTY`,`COINBASE`,`GASPRICE`,`BASEFEE` | block context | weak-randomness / front-running |
| `CODESIZE`,`EXTCODESIZE` | code size | the constructor-EOA / contract-existence check |
| `CALL`,`CALLCODE`,`DELEGATECALL`,`STATICCALL` | a foreign call | reentrancy / delegatecall / read-only-reentrancy |
| `SELFDESTRUCT` | selfdestruct | force-feed / library-kill |
| `CREATE`,`CREATE2` | deploy | the CREATE2 / constructor / lost-address |
| `SLOAD`,`SSTORE` | storage | the predicate's slots, the collision |
| `SHA3`/`KECCAK256` | a hash | a signature/answer/commit — check what's hashed |
| `REVERT`,`INVALID` | a revert | the guard's location — what it protects |
| precompile `0x01` (`ecrecover`) | a signature check | the signature class |
| `BALANCE`,`SELFBALANCE` | ether balance | the balance-predicate / force-feed |

## The reachability filter

Not every `SSTORE`-to-predicate-slot is reachable — the function may be
`onlyOwner`, `internal`, or behind an impossible `require`. The detection
narrows to: a `SSTORE` to the predicate's slot reachable from an `external`/
`public` function the supplied caller (or their deployed contract) can call.

## The source-vs-bytecode diff

```bash
cast code $CH --rpc-url $RPC > deployed.evm
solc --bin-runtime Challenge.sol > expected.evm     # may not match — the shipped source can differ
```

A mismatch → the bytecode is the truth: `heimdall decompile`, `panoramix`,
`evm disasm`. A challenge can ship a misleading source — the bytecode's
dispatch/SSTORE map is the real reachable surface.

## The predicate's slot chain

`isSolved()` `SLOAD`s the slots it reads. Trace which: `cast call $CH
"isSolved()(bool)"` on a fork + `forge`/`cast` the trace shows the SLOADs. The
slots it reads = the target. The functions that `SSTORE` those slots = the
candidate transitions.
