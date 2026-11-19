# Evasion — disguised and hardened web3 targets

## The obfuscation layers

| Layer | The effect | The counter |
|---|---|---|
| minified/single-letter names | the contract reads poorly | the bytecode + slot math still work; `cast storage` and the trace don't need names |
| bytecode-only (no source) | the logic is in the EVM ops | `cast code` + `heimdall`/`panoramix`/`evm disasm` decompile |
| a proxy hiding the impl | the real logic is behind the proxy | read the impl slot (`cast storage`), decompile the impl |
| a `selfdestruct`-scheduled trap | the contract disappears | solve before the destroy block; snapshot the bytecode early |
| a time-locked/hashed secret | the secret isn't directly readable | the storage read still leaks a hash — brute it, or find the path that bypasses the check |

## The anti-analysis

| Trick | The counter |
|---|---|
| a `delegatecall` to a hidden address | read the target slot with `cast storage`, then that target's code |
| assembly/`inline` blocks hiding logic | `evm disasm` the raw ops — `sload`/`sstore` reveal the slots touched |
| an `onlyOwner` on the WRONG field | the guard checks `tx.origin` or a settable var — bypass via that var |
| a decoy `isSolved()` that returns true early | the CHECKER's `isSolved()` is the real predicate — call the setup's, not a decoy |
| a honeypot-looking setter | `forge`/`cast` trace it — the revert/transfer that fires shows the trap |

## The decompile flow

```bash
cast code $CH --rpc-url $RPC > code.evm        # the runtime bytecode
evm disasm code.evm 2>/dev/null | head         # the raw ops
# heimdall decompile / panoramix — the readable pseudo-Solidity
```

The `sstore`/`sload` ops reveal which slots the code touches — the predicate's
slots and the functions that write them, without needing the source.

## The "the source lied" case

A challenge ships a `.sol` that doesn't match the deployed bytecode — the real
vulnerability is only in the bytecode. ALWAYS `cast code` and compare the
deployed bytecode's decompile to the shipped source; a mismatch means trust the
bytecode.

## The chain-opaque case

The flag isn't in a response — it's the checker reading `isSolved()`. There's no
"the response hides the flag" — the proof is the on-chain state change, which
can't be disguised: `cast call $SETUP "isSolved()(bool)"` is ground truth.
