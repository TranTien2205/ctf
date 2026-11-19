# Integer overflow / underflow — wrap the counter

## The shape

```solidity
pragma solidity ^0.7.0;             // pre-0.8: NO automatic checks
function transfer(uint _amt) public {
    require(balances[msg.sender] - _amt >= 0);    // unchecked arithmetic
    balances[msg.sender] -= _amt;
    balances[msg.sender] += _amt;                  // ... or a += that wraps
}
```

Solidity `<0.8` wraps arithmetic silently (the "SafeMath" era). `0 - 1` →
`2**256 - 1`. A `require` on the WRAPPED result passes, and the balance/accounting
becomes `2**256` — a drain or a predicate flip.

## The detection fingerprint

- `pragma solidity ^0.4 - ^0.7` (or `<0.8`) — silent wrap
- `unchecked { ... }` block in 0.8+ — the deliberate wrap
- arithmetic without `SafeMath`/`SafeMath`-free on an old pragma
- a `require(x - y >= z)` where the subtraction can wrap
- **falsifier**: `>=0.8` with no `unchecked` on the path — arithmetic reverts
  rather than wraps

## The exploit shapes

### Underflow → a huge balance

```solidity
balances[me] = 0;
transfer(1):  require(0 - 1 >= 0) → require(2**256-1 >= 0) passes
balances[me] = 2**256 - 1          → drain the contract
```

### Overflow → bypass a cap

```solidity
require(amount + fee <= limit);
amount = 2**256 - fee + 1  →  amount + fee wraps to 1 → require passes
```

### The batch-overflow (the BEC shape)

```solidity
function batchTransfer(address[] to, uint v) {
    uint total = v * to.length;        // overflows to a small number
    require(balances[me] >= total);    // passes on the wrapped total
    for (...) balances[to[i]] += v;    // each recipient gets the FULL v
}
```

## The 0.8 `unchecked` case

On `>=0.8` the compiler inserts wrap-checks that REVERT. The bug is then an
explicit `unchecked { }` block — find it, and the arithmetic inside wraps.
The detection is `unchecked` in source or a subtraction that doesn't revert
on the live bytecode.

## The accounting-integrity variant

Not a wrap — a **wrong invariant**: the contract tracks a `total` that a path
can desync from the real balance. Mint without crediting `total`, burn twice,
share-price arithmetic that rounds in the attacker's favour. The drain is a
withdraw that pays from the real balance against a lied-about `total`.

## The evidence

`cast call $CH "balances(address)(uint)" $ME` before/after — `0 → 2**256-1`;
`isSolved() → true` on the drain. The arithmetic and the balance read are the proof.
