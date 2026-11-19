# Front-running / ordering — win the race the contract leaves open

## The shape

```solidity
function claim(bytes32 answer) public {
    require(keccak256(abi.encode(answer)) == target);
    winner = msg.sender;                 // first correct answer wins
}
```

A pending transaction sits in the mempool; a contract that rewards the FIRST
correct call lets an observer copy the answer and submit it with a higher gas
price first. In CTF the "front-runner" is the supplied caller's own contract —
or the ordering dependency is in the contract logic, not the mempool.

## The detection fingerprint

- a first-come/claim/winner/auction/decision that rewards ordering
- `tx.gasprice`, block-position, or mempool-visible data feeding the win
- a two-step (commit then act) where the first step leaks the answer
- **falsifier**: a commit-reveal scheme (the answer is hashed until committed),
  or the decision isn't ordering-sensitive

## The exploit shapes

### Copy-and-outbid

Read the pending tx's calldata, re-send it with a higher gas price — the higher
gas lands first. Rarely needed in CTF (private chain, single player), but the
shape matters when a bot "claims" answers.

### The ordering-dependent invariant

The more common CTF shape: a function's result depends on CALL ORDER, and a
single transaction can force a specific order via a contract that sequences the
calls atomically. Two `claim`-then-`transfer` calls in one atomic tx, or a
flash-loan-style sequence, break an invariant the author assumed ran in order.

### The reorg / timestamp dependence

A `block.timestamp`-gated action — the supplied caller can't reorder the chain,
but a contract that bundles the read and the action in one tx pins them to the
same block.

## The commit-reveal boundary

The FIX is a hash-commit then reveal — the answer isn't visible until after the
commit window. If a challenge uses a plain `answer` param, the mempool (or a
contract that reads the public answer and calls) wins.

## The evidence

`isSolved() → true` after the ordering-forcing tx; the receipt shows the
calls landed in the needed order (one atomic contract tx guarantees it).
