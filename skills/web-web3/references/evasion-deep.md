# Evasion (deep) — the anti-analysis and the decoy contract

## The bytecode-only / obfuscation depth

| The layer | The counter |
|---|---|
| no `.sol` shipped — bytecode only | `cast code` + `heimdall`/`panoramix`/`evm disasm` → pseudo-Solidity |
| a proxy hiding the impl | `cast storage` the impl slot → read the impl's code |
| inline `assembly` hiding the logic | `evm disasm` the raw ops — `sstore`/`sload`/`delegatecall`/`selfdestruct` reveal it |
| single-letter/minified names | names don't matter — the slot positions and ops do |
| a `selfdestruct`-scheduled decoy | snapshot `cast code` early; solve before the destroy-block |

## The decoy patterns

| The decoy | The reality |
|---|---|
| a `isSolved()` that returns `true` early | the CHECKER's `isSolved()` is the real one — call the setup's |
| a `solve()`/`getFlag()` that returns a fake flag | the real flag is the platform's reward for `isSolved()` — not a contract return |
| a honeypot setter that reverts on a "trap" address | `cast run` the trace — the trap's condition names the safe address |
| a `private` var that's a red herring | the predicate's slots matter — a leaked secret that's not in the predicate is noise |
| a contract that LOOKS like the target | the setup's `challenge()` is the target — a decoy contract in the setup is noise |

## The decompile-and-verify flow

```bash
cast code $CH --rpc-url $RPC > code.evm
evm disasm code.evm > disasm.txt
# the dispatch table: PUSH4 <selector> ... EQ ... JUMPI → the reachable functions
# the SSTORE map: which slots each function writes
# the context ops: ORIGIN/CALLER/TIMESTAMP/DELEGATECALL/SELFDESTRUCT/ECRECOVER
# heimdall decompile code.evm  →  pseudo-Solidity
```

## The "the source lied" deeper case

A challenge ships a `.sol` whose logic differs from the deployed bytecode —
the real bug is only in the bytecode. The dispatch-table + SSTORE map reveals
the reachable surface the source hides. The bytecode is ALWAYS the truth.

## The "the contract is gone" case

A `selfdestruct`-scheduled contract — snapshot `cast code` + `cast storage`
early before the destroy block; a resurrect via CREATE2 to analyze the logic
offline. A challenge that destroys its own code needs the early snapshot.

## The chain-opaque case

The predicate's check isn't in a `.sol` — it's a separate verifier contract or
the platform's off-chain read of `isSolved()`. The on-chain state is ground
truth regardless — `isSolved()` reads the real state.
