# Common mistakes (deep) — the recurring errors with their fixes

## The simulation-confusion errors

| Mistake | The fix |
|---|---|
| a `cast call` result reported as the solve | `cast call` is a dry-run — send `cast send`, re-read `isSolved()` |
| a `forge test` pass as the solve | the fork is local — send on the live chain |
| a `cast call` returning the flag as the proof | the flag comes from the checker's live response, not the call |
| a solved-on-fork never sent live | the live `cast send` is the only solve |

## The state-assumption errors

| Mistake | The fix |
|---|---|
| reading a `private` var from the ABI | private vars aren't in the ABI — `cast storage` the slot |
| a `blockhash(block.number)` computed as non-zero | it's always `0` — the contract computes on `0` |
| a `blockhash` for a >256-old block | returns `0` — the "random" is `0` |
| reading the answer, then sending in a later block | the block changed — compute in the same tx (a Predict contract) |
| a `balance` assumed stable | the contract can be force-fed (`selfdestruct`) — the invariant breaks |

## The transaction errors

| Mistake | The fix |
|---|---|
| a `status: 0x0` treated as success | it reverted — `cast run` the trace |
| a mined-but-wrong-state tx | `status: 0x1` isn't the solve — `isSolved()` is |
| a tx from the wrong key | `cast wallet address --private-key $KEY` must match the `from` |
| a `value`-needing call sent without `--value` | the payable needs the funding |
| a contract deployed but `run()` never called | the deploy is the contract — the exploit is the `run()` tx |

## The contract-model errors

| Mistake | The fix |
|---|---|
| assuming `msg.sender` is the user | a contract in the middle makes it the contract — `tx.origin` |
| assuming `private` hides a secret | `cast storage` reads it |
| assuming `.transfer` lets a callback re-enter | 2300 gas — no room |
| assuming a `delegatecall` writes the callee's storage | it writes the CALLER's — by slot position |
| assuming an EOA can't call a contract during deploy | a constructor's `extcodesize == 0` |

## The detection errors

| Mistake | The fix |
|---|---|
| attacking before reading `isSolved()` | the predicate names the class — read it first |
| trusting the shipped `.sol` | `cast code` — the bytecode can differ |
| missing the reachable-function inventory | the unguarded setter is the enumeration's job |
| guessing a bug class the predicate doesn't point at | the predicate narrows to the classes that change its state |
