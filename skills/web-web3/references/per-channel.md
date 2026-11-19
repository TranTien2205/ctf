# Per-channel map — the interaction channel → the check

## The channels

| Channel | The use |
|---|---|
| `eth_call` (`cast call`) | the free read — simulate a call, no state change |
| `eth_sendTransaction` (`cast send`) | the attributable write — the solve |
| `eth_getStorageAt` (`cast storage`) | the slot read — `private` vars too |
| `eth_getBalance` (`cast balance`) | the ether read |
| `eth_getCode` (`cast code`) | the bytecode read |
| `eth_getTransactionReceipt` (`cast receipt`) | the receipt — the mined proof |
| `eth_getTransactionByHash` (`cast tx`) | the tx — the calldata + the from |
| `eth_getLogs` (`cast logs`) | the emitted events |
| `eth_call` with a block tag | a historical-state read |
| `debug_traceTransaction` (`cast run`) | the execution trace |

## The free-vs-attributable split

| Free (eth_call + reads) | Attributable (eth_sendTransaction) |
|---|---|
| `cast call`, `cast storage`, `cast balance`, `cast code`, `cast logs`, `cast tx`, `cast receipt`, `cast chain-id`, `cast nonce` | `cast send`, `forge create`, `cast send --create` |

The free reads are the iteration surface — enumerate, dry-run, verify. The
attributable `cast send` is the solve — the last step.

## The block-tag channel

`cast call $CH "fn()" --block <N>` reads the state at block N — the historical
state. Useful for a multi-tx analysis; the solve's verify reads the LATEST block.

## The trace channel

`cast run <txhash>` / a `debug_traceTransaction` — the opcode-level execution:
which `SSTORE`s ran, which `require` fired, the call stack. The revert-reason
and the state-change trace.

## The channel-to-evidence map

| Channel | The evidence it produces |
|---|---|
| `cast call isSolved()` | the predicate flip — false → true |
| `cast receipt` | the mined-tx proof — status/from/to |
| `cast storage` | the slot before/after |
| `cast run` | the execution trace — the mechanism |
| `cast tx` | the calldata + the attribution |

## The channel the checker uses

The checker reads `isSolved()` via `eth_call` — the solve's proof is the state
that call reads. The flag is the platform's response to the `true` predicate —
not a `cast` output.
