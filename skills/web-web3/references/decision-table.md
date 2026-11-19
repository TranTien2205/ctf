# Decision table — observation → the next call

| Observation | The next call |
|---|---|
| `isSolved()` reads `owner()` | enumerate owner-setters; `cast send "setOwner"` if unguarded |
| `isSolved()` reads `balance` | the withdraw + the ether routes; reentrancy or force-feed |
| a bare `setOwner`/`unlock`/`setFlag` | `cast send` it — the cheap solve |
| `tx.origin` in a check | deploy a Phish contract, the caller calls `attack` |
| `delegatecall` in a fallback | read the impl slot; check the layouts; call through the proxy |
| `call{value}` then `-=` | deploy a `receive`-reenter; deposit+withdraw |
| `pragma <0.8`, no SafeMath | the transfer/arithmetic that wraps |
| `block.timestamp`/`blockhash` in a decision | deploy a Predict contract, the same-block answer |
| `selfdestruct` reachable / a `balance` predicate | funded Force deploy + `boom` |
| `initialize`/`init` callable | `cast send "initialize(address)" $ME` |
| a `private` secret gate | `cast storage` the slot → feed it to the gate |
| `ecrecover` + a replayable hash | the replayed/forged sig |
| `deposit`/`withdraw`/`rate` | the desync: donation, first-deposit, reentrancy |
| a `for` over a growing array | grow it past the gas limit — the DOS |
| `winner`/`claim`/`auction` | a contract that sequences the calls atomically |
| `extcodesize == 0` check | call from a contract's constructor |
| a bytecode-only contract | `cast code` + `evm disasm`/decompile → the SSTORE map |
| a revert on the planned call | `cast run <tx>` the trace → the failing require |
| `isSolved()` still false after a mined tx | the wrong transition — re-read the predicate |
| every reachable fn enumerated, none writes the slot | the class is falsified → escalate |
