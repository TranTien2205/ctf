# Common mistakes — the errors that burn web3 attempts

## The confirm traps

| Mistake | Why it fails |
|---|---|
| claiming a `forge test` pass as a solve | the fork is local — the live chain is unchanged |
| a `cast call` simulation treated as the solve | `call` is a dry-run — no state change |
| a `status: 0x0` tx treated as success | it REVERTED — the state didn't change |
| a mined-but-no-op tx | `status: 0x1` but `isSolved()` still false — the wrong transition |
| reusing a previous instance's address/key | the challenge is per-instance — read the live setup |
| recording the private key in notes | it's a credential — record that it was used, not its value |

## The detection traps

| Mistake | Why it fails |
|---|---|
| attacking before reading `isSolved()` | the predicate names the class — attacking blind burns the budget |
| assuming the shipped `.sol` is the deployed code | diff `cast code` — the bytecode may differ |
| reading a `private` var from the ABI | private vars aren't in the ABI — use `cast storage` |
| guessing the function signature | use `cast` with the exact Solidity signature, or `cast 4byte` to resolve a selector |

## The exploit traps

| Mistake | Why it fails |
|---|---|
| a reentrancy on a `.transfer` (2300 gas) | not enough gas to re-enter — the guard holds |
| a `msg.sender` exploit needing `tx.origin` | a contract in the middle changes the caller chain |
| a delegatecall without matching storage layout | the write lands on a different slot |
| an overflow on `>=0.8` (no `unchecked`) | the arithmetic REVERTS, doesn't wrap |
| a `selfdestruct` on a same-tx-created contract | post-Cancun it may not fully delete |
| sending ether to a contract that reverts in `receive` | `call{value}` fails — but `selfdestruct` force-feeds anyway |
| a signature replay on a bound hash | the nonce/chainid/sender binding makes it invalid |

## The discipline traps

| Mistake | Why it fails |
|---|---|
| many transactions guessing at the transition | each tx is attributable + permanent — enumerate the reachable calls first |
| a sixth variant of a reverted call | budget spent — `decide.py escalate`, a different transition or class |
| treating the "obvious" access-control as too easy | the bare setter IS often the intended solve — check it first |
| a chain without per-step evidence | the final `isSolved()` doesn't prove the intermediate steps |

## The cleanup traps

| Mistake | Why it fails |
|---|---|
| leaving an attack contract unfunded | a `payable` exploit needs the deploy to carry `value` |
| not recording the tx hash | the receipt is the proof — `cast tx` / `cast receipt` preserve it |
