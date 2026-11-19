# Workflow playbook — the per-class decision sequence

## The "is it web3" gate

```
.sol / Setup.sol / an RPC endpoint / isSolved() → YES, this class
no contract, just HTTP → not this class
```

## The class decision tree

```
read isSolved()
  ├─ reads owner()/a caller check
  │    ├─ a bare setter exists            → access-control → cast send
  │    ├─ the guard is tx.origin          → tx.origin → Phish contract
  │    ├─ the guard is msg.sender==origin  → constructor call (extcodesize 0)
  │    └─ the slot is writable via delegatecall → delegatecall/storage-collision
  ├─ reads balance/address(this).balance
  │    ├─ a call-then-update withdraw      → reentrancy → attack contract
  │    ├─ the contract refuses ether       → selfdestruct force-feed
  │    └─ a rate/shares desync             → accounting-vault
  ├─ reads flag/locked/solved
  │    ├─ a bare setter                    → access-control
  │    ├─ a private-var gate               → visibility → cast storage
  │    └─ a delegatecall writes the slot   → delegatecall
  ├─ reads answer/winner/guess
  │    ├─ block.* feeds the answer         → weak-randomness → Predict contract
  │    └─ a first-come/ordering            → front-running → atomic contract
  ├─ reads count/balances[x]
  │    ├─ <0.8 arithmetic                  → integer-overflow
  │    └─ a callable-increment reentrancy  → reentrancy
  ├─ reads code.length/extcodesize
  │    └─ selfdestruct / the constructor-EOA trick
  └─ reads signer/verified
       └─ a replayable/malleable hash      → signature
```

## The transition decision

```
ONE class named → the primitive → the transition:
  bare-class     → one cast send
  contract-class → write + deploy + run the attack contract
  atomic-class   → a Solver.run() sequencing the steps
```

## The verify decision

```
cast send → cast receipt (status 0x1, from caller) → cast call isSolved() → true
  → the solve; record the chain
isSolved() still false → the wrong transition → re-read the predicate
```

## The escalate decision

```
3 reverted txs / every reachable writer enumerated and guarded / the falsifier observed
  → decide.py escalate → a different class or a different contract in the setup
```
