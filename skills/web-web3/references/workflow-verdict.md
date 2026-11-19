# Workflow verdict — when each phase is done

## The done-criteria

| Phase | Done when |
|---|---|
| intake | the RPC + caller confirmed live; `isSolved()`'s expression recorded |
| predicate | the target state named — which slots/reads to change |
| state-map | the getters + slots + balance captured |
| inventory | every non-view external/public function listed + its writes marked |
| class | ONE class named — the predicate + a reachable transition |
| plan | ONE transition written — the `cast send` or the attack contract |
| dry-run | `forge`/`call` sim flips the simulated `isSolved()` |
| send | `cast send` mined — `status: 0x1`, `from` = the caller |
| verify | `isSolved()` → `true` on the live chain + the receipt preserved |

## The "stuck in a phase" rules

- **stuck in detection** → the predicate + the reachable calls — re-read
  `isSolved()`; a wrong class guess is the common cause
- **stuck in plan** → the transition that writes the predicate's slot — the
  inventory has it or the class is closed
- **stuck in send** → the revert reason — `cast run` the trace
- **stuck in verify** → `isSolved()` still false — the wrong transition

## The escalate verdict

3 reverted txs on the same transition, or the reachable-writers enumeration
closed → `decide.py escalate`. The web3 budget is in transactions — a wrong
class guess is the common cause; a different contract in the setup is the
common fix.

## The solve verdict

`isSolved() → true` + the receipt `status: 0x1` + `from` = the supplied caller
+ the platform's flag returned — the solve is verified; record the chain.
