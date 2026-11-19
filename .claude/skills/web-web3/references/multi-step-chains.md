# Multi-step chains — when the solve needs more than one bug

## The single-bug case first

Most CTF web3 is one reachable transition — a bare setter, one reentrancy, one
delegatecall. Confirm the cheap case before building a chain.

## The two-bug patterns

| Chain | The sequence |
|---|---|
| **access → reentrancy** | become owner (unguarded setter) → call the owner-gated `withdraw` that reenters |
| **collision → delegatecall** | `setA` writes proxy slot0 (impl) → now `impl` = attacker code → next call delegates to it |
| **visibility → access** | `cast storage` the private password → `unlock(password)` the access gate |
| **weak-rand → claim** | Predict contract computes the answer → `guess(answer)` claims |
| **force-feed → drain** | `selfdestruct` forces ether in → a balance check passes → then a reentrancy drains |
| **init → selfdestruct** | `initialize` owns the library → `kill` selfdestructs the caller's context |

## The attack-contract pattern

The exploit is usually a deployed contract, not raw `cast send` calls:

```solidity
contract Solver {
    Target t;
    constructor(address _t) { t = Target(_t); }
    function run() external payable {
        // the sequence — atomic in one tx where ordering matters
        t.step1();
        t.step2{value: msg.value}();
        t.step3();      // the predicate flips inside this atomic tx
    }
}
```

An atomic sequence guarantees ordering — a `step1 → step2` that must land in the
same block goes in one `run()`. Non-atomic steps are separate `cast send`s.

## The sequencing decision

- **atomic** (one contract `run()`): when the steps must share a block/ordering —
  front-running, flash-loan, a mid-state a third party could steal
- **separate txs**: when the steps are independent state changes — init then
  claim; cheaper to debug per-step

## The evidence per step

Each step's `cast call`/storage read before/after proves that transition; the
final `isSolved()` read + the tx hashes prove the chain. Preserve the order and
each receipt — a chain's proof is the ordered sequence, not the last tx alone.

## The falsifier

A step in the chain reverts on a state its predecessor didn't reach → the chain
ordering is wrong or a step's precondition isn't met. Re-read the reverted
`require`; the predecessor must set the state it checks.
