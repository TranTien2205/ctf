# First hour — the bounded opening

## The first ten minutes

```bash
export RPC=<rpc> KEY=<privkey>
cast chain-id --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC      # the predicate, expect false
cast call $SETUP "challenge()(address)" --rpc-url $RPC  # the target address
```

Then read `Setup.sol` + `Challenge.sol` — `isSolved()`'s expression names the
class before a single transaction.

## The read pass (minutes 10–25)

```bash
CH=<challenge-addr>
cast call $CH "owner()(address)" "locked()(bool)" --rpc-url $RPC   # the getters
cast balance $CH --rpc-url $RPC
for s in 0 1 2 3 4; do cast storage $CH $s --rpc-url $RPC; done    # the slots
cast code $CH --rpc-url $RPC | head -c 200                          # the bytecode exists
```

Map the reachable non-view functions; mark which write the predicate's slots.
The unguarded setter is usually the solve — check it before the deep bug.

## The class decision (minutes 25–40)

`attack-shapes.md`: the predicate shape → the likely class → the file. The
reachable-function inventory + the source signals (`detection-map.md`) confirm
the transition. Write the ONE planned `cast send` (or the attack contract).

## The dry-run (minutes 40–50)

`forge test --fork-url $RPC` the exploit, or `cast call` it as a dry-run —
the simulated `isSolved()` should flip. A sim-fail is free; fix the transition.

## The send + verify (minutes 50–60)

```bash
cast send $CH "<sig>" <args> --private-key $KEY --rpc-url $RPC
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC      # false → true = solved
cast receipt <txhash> --rpc-url $RPC                    # status 0x1, from = caller
```

The solve is `isSolved() → true` on the live chain + the receipt. Preserve the
tx hash, the calldata, and the before/after reads.

## The discipline line

If the first class's transition reverts 3 times with no new revert reason →
`decide.py escalate`. The web3 budget is in transactions — the iteration lives
in the read/dry-run, not in sent transactions.
