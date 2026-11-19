# Detection checklist — the web3 class confirmed

## The package check

- [ ] a `*.sol` file or a deployed contract address is present
- [ ] a `Setup.sol`/`isSolved()` or an equivalent solved predicate exists
- [ ] an RPC endpoint + a private key (or a way to send transactions)
- [ ] `cast chain-id` confirms the live chain

## The predicate check

- [ ] `isSolved()`'s exact expression recorded
- [ ] the predicate's slots/reads named — which state the checker needs
- [ ] the predicate shape mapped to a class (`attack-shapes.md`)

## The reachability check

- [ ] the external/public non-view functions enumerated
- [ ] each checked: does it write a predicate slot? is it guarded?
- [ ] the deployed bytecode checked (`cast code`) against the source
- [ ] the caller's deployable-contract surface considered (Phish/Predict/Force)

## The state check

- [ ] `cast call` the predicate-relevant getters — starting values
- [ ] `cast storage` the low slots — the `private` and the predicate vars
- [ ] `cast balance` the contract — the ether surface
- [ ] `cast logs`/`cast tx` — emitted secrets, constructor args

## The falsifier check

- [ ] at least one reachable transition can satisfy the predicate
- [ ] the class's falsifier NOT observed — the path is open
- [ ] the negative-results recorded for the dead paths

## The class decision

- [ ] ONE class named with the predicate + the reachable call
- [ ] the planned transition written (the `cast send` or the attack contract)
- [ ] `decide.py`/`hooks.py` the checkpoint before the attributable send
