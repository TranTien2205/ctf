# Workflow (deep) — the full operation from package to receipt

## Phase 0 — package intake

```bash
ls                              # Setup.sol, Challenge.sol, an RPC URL, a key
export RPC=<rpc> KEY=<privkey>
cast chain-id --rpc-url $RPC
cast wallet address --private-key $KEY   # the attributable caller
```

Read `Setup.sol` FIRST — the `isSolved()` predicate names the target.

## Phase 1 — the predicate analysis

```solidity
isSolved() → the exact boolean: owner()==X / balance==0 / flag / locked==false
```

The predicate names the class — `attack-shapes.md`. Record:
- the predicate's exact expression
- the challenge address (`setup.challenge()` or the deploy log)
- every contract the setup deploys

## Phase 2 — the state map

```bash
CH=<challenge>
cast call $CH "owner()(address)" "locked()(bool)" "isSolved()(bool)" --rpc-url $RPC
cast balance $CH --rpc-url $RPC
for s in 0 1 2 3 4 5; do cast storage $CH $s --rpc-url $RPC; done
cast code $CH --rpc-url $RPC | wc -c     # bytecode exists; decompile if no source
```

## Phase 3 — the reachable-call inventory

List every external/public non-view function. For each:
- does it `SSTORE` a predicate slot? → candidate
- is it guarded, and by what? → the access check
- does it `call`/`delegatecall`/`selfdestruct` before settling? → the primitive

## Phase 4 — the class + the transition

`attack-shapes.md` / `per-bug.md` map the predicate + the reachable calls to
the bug class. Write the ONE planned transition — a `cast send`, or an attack
contract's `run()`.

## Phase 5 — the dry-run

```bash
forge test --fork-url $RPC       # or: cast call the exploit as a dry-run
```

The simulated `isSolved()` should flip. A sim-fail is free — fix the transition.

## Phase 6 — the attributable send

```bash
cast send $CH "<sig>" <args> --private-key $KEY --rpc-url $RPC
# or the attack contract:
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
cast send $SOLVER "run()" --private-key $KEY --rpc-url $RPC
```

## Phase 7 — the verify + record

```bash
cast call $SETUP "isSolved()(bool)" --rpc-url $RPC   # false → true
cast receipt <txhash> --rpc-url $RPC                  # status 0x1, from = caller
cast tx <txhash> --rpc-url $RPC
```

Preserve: the predicate expression, the calldata, the tx hash, the receipt, the
before/after reads. The flag is what the checker returns on `isSolved() == true`.

## The failure re-order

A revert → `cast run <txhash>`/`forge` the trace → the failing `require` → the
unmet precondition → a different transition or the predecessor that sets it.
3 reverts with no new reason → `decide.py escalate`.
