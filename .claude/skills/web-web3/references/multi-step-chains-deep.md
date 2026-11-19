# Multi-step chains (deep) — the composed-exploit reference

## The chain types

### Setup-then-exploit

```solidity
// step 1: become owner / set the impl / pass the gate
// step 2: the gated action that flips the predicate
contract S { function run() external {
    t.setOwner(me);            // unguarded — step 1
    t.withdraw();              // owner-gated — step 2, now callable
}}
```

### Collision-then-delegatecall

```solidity
// step 1: a collision write changes proxy's impl to attacker code
// step 2: the next delegatecall runs attacker code → write owner / selfdestruct
contract S { function run() external {
    proxy.setA(address(evil));          // collision → impl = evil
    proxy.fallback(evil.pwn.selector);   // delegatecall evil.pwn → writes owner
}}
```

### Init-then-kill

```solidity
// step 1: initWallet the library → own its context
// step 2: kill → selfdestruct the calling contract
```

### Force-feed-then-drain

```solidity
// step 1: force-feed ether to a contract the predicate checks
// step 2: a reentrancy/withdraw drains it — or the balance-check passes
```

### Predict-then-claim

```solidity
// step 1: the Predict contract computes the same-block answer
// step 2: it calls guess(answer) in the same tx — atomic
```

## The atomicity decision

- **atomic** (one `run()`): the steps must share a block/order — a front-run
  target, a check-then-act, a mid-state a third party could steal
- **separate txs**: independent state changes — cheaper to debug per-step, but
  the chain's per-step evidence must still be preserved

## The chain's evidence

Each step's `cast call`/storage read before/after proves that transition; the
final `isSolved()` + the ordered tx hashes prove the chain. Preserve the order —
a chain's proof is the sequence, not the last tx.

```text
deploy Solver (funded if payable)      → the contractAddress
tx1: step1()                           → the receipt + the getter read
tx2: step2()                           → the receipt + the getter read
final: cast call isSolved() → true     → the solve
```

## The failure-point isolation

A step reverts → `cast run` the trace → the failing `require` → its
precondition is the predecessor's job — a step that didn't set the state the
next reads. The chain's order or a missing predecessor is the bug.

## The compose-when-needed rule

Don't build a chain when a single transition solves — enumerate the reachable
writers first; the bare setter is the solve. A chain exists only when no single
transition reaches the predicate.
