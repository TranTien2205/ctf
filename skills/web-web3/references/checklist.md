# Checklist — the web3 solve, step by step

## Intake

- [ ] `Setup.sol` + `Challenge.sol` + RPC + private key present
- [ ] `cast chain-id` confirms the live chain
- [ ] `cast wallet address --private-key $KEY` = the attributable caller
- [ ] `isSolved()` read — the predicate's exact expression recorded
- [ ] the challenge address resolved (`setup.challenge()` or the deploy log)

## Detection

- [ ] the predicate shape mapped to the class (`attack-shapes.md`)
- [ ] the reachable non-view functions enumerated
- [ ] each function checked: does it `SSTORE` a predicate slot? is it guarded?
- [ ] the deployed bytecode checked against the source (`cast code`)
- [ ] the low storage slots read (`cast storage 0..N`)
- [ ] the starting state captured (getters + balance)

## Exploit

- [ ] ONE transition named — the cheapest reachable write
- [ ] the attack contract written if the primitive needs it (reentrancy/phish/force)
- [ ] dry-run on `forge --fork-url`/`cast call` — the sim `isSolved()` flips
- [ ] `cast send` from the supplied caller — attributable
- [ ] a `payable` exploit funded on deploy/send

## Verify

- [ ] `cast receipt <txhash>` — `status: 0x1`, `from` = caller
- [ ] `cast call $SETUP "isSolved()(bool)"` → `true` (was `false`)
- [ ] the flag recorded from the checker's live response
- [ ] the tx hash, calldata, receipt, before/after reads preserved

## Discipline

- [ ] read-only enumeration BEFORE the first transaction
- [ ] the private key never recorded
- [ ] a `call`/`forge` sim never recorded as a solve
- [ ] 3 reverted txs → `decide.py escalate`
