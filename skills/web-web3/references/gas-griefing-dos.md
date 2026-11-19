# Gas griefing / denial of service — break the contract's own operation

## The shapes

| Shape | The exploit |
|---|---|
| **the unbounded loop** | a function iterates a caller-extensible array — grow it until the loop runs out of gas for everyone |
| **the refusing partner** | a `King`/`partner` contract that reverts in `receive` — the contract can't pay it, so it can't proceed |
| **the gas-griefing call** | a `call` that forwards too little gas — the callee's needed op runs out |
| **the block-stuffing** | fill the block so a needed tx can't land — rare in a private chain |
| **the selfdestruct-poison** | force-feed ether to break a `balance == 0` invariant the contract depends on |

## The "King" shape

```solidity
function claim() payable {
    require(msg.value > current);
    payable(king).transfer(current);   // pays the old king
    king = msg.sender;
}
```

Become `king` with a contract that REVERTS in `receive` — the next `claim`
fails on the `transfer` to it → the attacker stays king forever → `isSolved`
reads `king == attacker`. The fix is a `call` that tolerates the revert or a
pull-payment pattern; the bug is the `transfer` the contract depends on.

## The "Denial" shape

```solidity
function withdraw() {
    partner.call{value: share}("");   // the partner is a contract
    // partner's receive() burns all gas / reverts → withdraw always fails
}
```

Become `partner` with a contract whose `receive` burns all gas (an infinite
loop) or reverts → the contract's `withdraw` can never complete → DOS.

## The unbounded-loop shape

```solidity
function distribute() external {
    for (uint i; i < members.length; i++) pay(members[i]);   // members grows unbounded
}
```

Add enough `members` (via a public `join`) that the loop's gas exceeds the
block limit → `distribute` can never run → a payable/needed function is bricked.

## The detection fingerprint

- a `for`/`while` over a caller-extensible array/mapping
- a `call`/`transfer` to a caller-supplied address the contract depends on
- a `king`/`partner`/`owner` the contract pays and that can revert
- **falsifier**: a pull-payment pattern (the contract doesn't push), a bounded
  loop, or the revert is tolerated

## The invariant-break shape

Some "DOS" is a predicate-flip: the contract must maintain `balance > 0` or
`owner == setup`; a `selfdestruct` force-feed or a `claim` that flips it is the
exploit. The DOS is the means; the predicate is the end.

## The evidence

`isSolved() → true`, or the contract's needed function provably can't run (the
`cast call` to it reverts). The attack contract's deploy + the tx that became
the refusing partner / grew the loop are the chain.
