# Field manual catalogue — the operation, indexed by phase

## Phase 0 — intake (recon-order.md)

```bash
export RPC=<rpc> KEY=<privkey>
cast chain-id; cast wallet address --private-key $KEY; cast balance $ME
cat Setup.sol    # the predicate + the deploys
```

Done when: the RPC + caller confirmed live, `isSolved()`'s expression recorded.

## Phase 1 — the predicate (detection.md, attack-shapes.md)

```bash
cast call $SETUP "isSolved()(bool)"    # → false
cast call $SETUP "challenge()(address)"
```

Done when: the target state named — which slots/reads to change — and the class
the predicate's shape points at.

## Phase 2 — the state map (detection-surface.md)

```bash
cast call $CH "owner()(address)" "locked()(bool)"    # the getters
for s in 0 1 2 3 4 5; do cast storage $CH $s; done   # the slots
cast balance $CH; cast code $CH | head -c 100
cast logs --rpc-url $RPC "address=$CH"
```

Done when: the starting state captured — the getters, the slots, the balance,
the bytecode-exists check, the emitted secrets.

## Phase 3 — the inventory (detection-deep.md, per-verb.md)

```bash
grep -nE "function .*\(.*\).*(public|external)" Challenge.sol
grep -nE "delegatecall|tx.origin|block\.|selfdestruct|ecrecover|unchecked|private|call" Challenge.sol
# or the bytecode: cast code | evm disasm | grep PUSH4/SSTORE/DELEGATECALL/SELFDESTRUCT
```

Done when: every reachable non-view function listed, each marked with whether
it writes a predicate slot and how it's guarded.

## Phase 4 — the class + the plan (attack-shapes.md, per-bug.md, payload-map.md)

Done when: ONE class + ONE transition + the falsifier — the `cast send` or the
attack contract written.

## Phase 5 — the dry-run (workflow.md, exploitation.md)

```bash
forge test --fork-url $RPC -vvvv   # or cast call the dry-run
```

Done when: the sim's `isSolved()` flips — the transition is confirmed pre-send.

## Phase 6 — the send (exploitation-deep.md, payload-variants.md)

```bash
cast send $CH "fn(args)" <args> --private-key $KEY --rpc-url $RPC
forge create Solver --constructor-args $CH --private-key $KEY --rpc-url $RPC
```

Done when: the attributable tx mined — `status: 0x1`.

## Phase 7 — the verify + record (evidence-rules.md, verification-protocol.md)

```bash
cast call $SETUP "isSolved()(bool)"   # → true
cast receipt <txhash>; cast tx <txhash>; cast run <txhash>
```

Done when: `isSolved() → true` + the receipt `from` = the caller + the chain
preserved + `hooks.py post-probe` + the flag recorded.
