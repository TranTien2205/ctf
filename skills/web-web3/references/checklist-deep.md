# Checklist (deep) — the complete web3 operation

## Phase 0 — intake

- [ ] `Setup.sol`/`Challenge.sol` + RPC + key present
- [ ] `cast chain-id`, `cast wallet address` — the live chain + the caller
- [ ] `cast balance $ME` — the caller has funds if the exploit needs value
- [ ] `isSolved()`'s exact expression recorded — the predicate

## Phase 1 — the state map

- [ ] the challenge address resolved
- [ ] `cast call` the predicate getters — the starting values
- [ ] `cast storage` the low slots (0–N) — the `private` + predicate vars
- [ ] `cast balance` the contract — the ether surface
- [ ] `cast code` — bytecode matches the source? decompile if not
- [ ] `cast logs`/`cast tx` — emitted secrets, constructor args
- [ ] every contract the setup deploys mapped

## Phase 2 — the inventory

- [ ] every non-view external/public function listed
- [ ] each marked: writes a predicate slot? guarded? by what?
- [ ] the `call`/`delegatecall`/`selfdestruct`/`create` ops noted
- [ ] the `block.*`/`tx.origin`/`ecrecover`/`private` signals noted
- [ ] the pragma + `unchecked`/`SafeMath` checked

## Phase 3 — the class + the transition

- [ ] the predicate → the class (`attack-shapes.md`)
- [ ] the reachable call → the transition (`per-bug.md`)
- [ ] the class's falsifier checked — the path is open
- [ ] ONE transition planned — the `cast send` or the attack contract
- [ ] the attack contract written if the primitive needs it

## Phase 4 — the dry-run + send

- [ ] `forge test --fork-url`/`cast call` — the sim flips `isSolved()`
- [ ] a `payable` exploit funded
- [ ] `cast send` / `forge create` + `run` — attributable
- [ ] the tx hash + the receipt captured

## Phase 5 — the verify + record

- [ ] `cast call $SETUP "isSolved()(bool)"` → `true` (was `false`)
- [ ] `cast receipt` — `status: 0x1`, `from` = the caller
- [ ] `cast run <tx>` the trace preserved
- [ ] the calldata + the before/after reads + the tx hash recorded
- [ ] `hooks.py post-probe --verdict confirms` the solve
- [ ] the private key never recorded

## The stop/escalate

- [ ] 3 reverted txs on one transition → `decide.py escalate`
- [ ] the reachable-writers enumeration closed → escalate to a different contract
- [ ] the solve verified → record the chain card + `classify_solve.py`
