# Common questions catalogue — every recurring question indexed

## The "is it solved" questions

| Question | The answer | File |
|---|---|---|
| `isSolved()` was already true — did I solve it? | no — a stale read or a pre-solved setup | `common-questions.md` |
| a `cast call` returned true — did I solve it? | no — a dry-run; `cast send` it live | `common-questions.md`, `evidence-rules.md` |
| `forge test` passed — did I solve it? | no — a local fork; `cast send` on the live chain | `evidence-rules.md` |
| `status: 0x1` — did I solve it? | not necessarily — check `isSolved()` after | `troubleshoot.md` |
| the tx mined but `isSolved()` is false | the wrong transition — re-read the predicate | `troubleshoot.md`, `common-questions.md` |

## The "how do I" questions

| Question | The answer | File |
|---|---|---|
| read a `private` variable? | `cast storage $CH <slot>` | `visibility.md` |
| send a payable call? | `cast send ... --value <amt>` | `exploitation.md` |
| deploy a contract? | `forge create`/`cast send --create` | `exploitation-deep.md` |
| read the contract's bytecode? | `cast code` | `detection-deep.md` |
| decompile bytecode? | `evm disasm`/`heimdall`/`panoramix` | `evasion.md` |
| compute a mapping slot? | `cast index`/`cast keccak` | `storage-collision-deep.md` |
| force ether into a contract? | `selfdestruct` — `selfdestruct.md` |
| recover a lost contract address? | `cast getAddress`/the deploy tx | `per-target.md` |

## The "why won't it" questions

| Question | The answer | File |
|---|---|---|
| the reentrancy doesn't re-enter? | `.transfer`/`.send`/`nonReentrant` | `reentrancy-map.md` |
| the overflow doesn't wrap? | `>=0.8`/SafeMath/no unchecked | `integer-overflow-map.md` |
| the `cast storage` returns `0x`? | a hashed slot — `cast index`/`keccak` | `troubleshoot.md` |
| the sig won't validate? | the hash fields/prefix bound it | `signature-replay-map.md` |
| the tx reverts? | `cast run` the trace — the failing require | `troubleshoot.md`, `troubleshoot-deep.md` |
| a contract won't accept ether? | it can't refuse `selfdestruct` — `selfdestruct.md` |

## The "where do I look" questions

| Question | The answer | File |
|---|---|---|
| no obvious vulnerability? | enumerate the reachable functions; the bare setter first | `common-questions.md` |
| the setup deploys several contracts? | the predicate's is the target; map the rest | `common-questions-deep.md` |
| only bytecode, no source? | `cast code` + disasm → the dispatch/SSTORE map | `detection-deep.md` |
| a decoy source? | the bytecode is the truth | `evasion.md` |
