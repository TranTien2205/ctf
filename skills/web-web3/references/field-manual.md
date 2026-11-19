# Field manual — the operational summary

## The one-paragraph class

A `Setup.sol` ships a `Challenge.sol` and an `isSolved()` predicate on a private
chain. Reach the predicate's state with a transaction from the supplied caller.
Read `isSolved()` first — it names the class. Enumerate the reachable non-view
functions; the one that writes the predicate's slot unguarded is the cheapest
solve. `cast call`/`storage`/`balance` free, `cast send` attributable + permanent.

## The decision table

| If the predicate reads | The class | The file |
|---|---|---|
| `owner()`/`msg.sender` | access-control / tx.origin | `access-control.md`/`tx-origin.md` |
| `balance`/`address(this).balance` | reentrancy / selfdestruct | `reentrancy.md`/`selfdestruct.md` |
| `balances[x]`/`count` | integer-overflow / accounting | `integer-overflow.md` |
| `locked()`/`flag`/`solved` | access-control / visibility | `access-control.md`/`visibility.md` |
| `answer`/`guess`/`winner` | weak-randomness / front-running | `weak-randomness.md` |
| `code.length`/`extcodesize` | selfdestruct / constructor | `selfdestruct.md`/`edge-cases.md` |

## The command sheet

```bash
# READ
cast call $SETUP "isSolved()(bool)"
cast call $CH "owner()(address)"
cast storage $CH 0
cast balance $CH
cast code $CH
cast chain-id; cast block-number

# DEPLOY
cast send --create "<bin>" --value 1ether --private-key $KEY --rpc-url $RPC
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC

# WRITE
cast send $CH "fn(args)" <args> --private-key $KEY --rpc-url $RPC

# VERIFY
cast call $SETUP "isSolved()(bool)"
cast receipt <txhash> --rpc-url $RPC
```

## The discipline

- enumerate reachable functions BEFORE the first transaction
- the bare setter is often the intended solve — check it first
- a `private` var is not a secret — `cast storage` reads it
- `cast call`/`forge` is a simulation — only `cast send` flips live state
- the receipt's `status: 0x1` + `isSolved()` true = the solve; neither alone
- the private key never goes in notes
- `decide.py escalate` after 3 reverted txs on one transition

## The pointer set

- the class map: `attack-shapes.md`, `per-bug.md`, `detection-map.md`
- the primitives: `evm-primitives.md`, `mechanism.md`
- the workflow: `workflow.md`, `first-hour.md`, `exploitation.md`
- the evidence: `evidence-rules.md`, `negative-results.md`, `verified-chains.md`
