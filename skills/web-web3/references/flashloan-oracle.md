# Flash loans / oracle manipulation — the atomic-skew class

## The flash-loan primitive

A lending contract that lends `amount` for the duration of ONE transaction — the
borrower must repay `amount + fee` by the tx's end or the whole tx reverts. The
borrowed capital is a temporary balance the exploit uses then returns.

```solidity
function attack() external {
    pool.flashLoan(amount);          // pool calls back into this contract
}
function onFlashLoan(amount, fee) external {   // the callback
    // use `amount` for the skew — in the SAME tx
    vulnerable.exploitThatReadsBalance();
    pool.repay(amount + fee);        // repay — keep the skimmed profit
}
```

## The oracle-manipulation shape

A contract that reads a PRICE from a manipulable source — an AMM's reserve
ratio, an on-chain oracle, a spot price:

```solidity
uint price = reserve1 / reserve0;    // a spot price — manipulable by a big swap
// or: price = oracle.getPrice();    // the oracle's source is manipulable
```

The exploit: a flash-loaned swap moves the AMM's reserves → the spot price
spikes → a contract that prices on it over/under-pays → repay the loan, keep
the difference.

## The single-block / same-tx requirement

The skew must happen in the SAME transaction as the vulnerable call — the loan
is atomic. A contract that sequences the loan + the vulnerable call + the repay
in one tx is the standard exploit shape.

## The shapes

| Shape | The exploit |
|---|---|
| **spot-price oracle** | a big flash-loan swap moves the reserve → the price the contract reads is skewed → buy cheap / sell dear |
| **balance-read decision** | the contract decides on `balanceOf(this)` — a flash-loan deposit inflates it for the decision block |
| **governance/flash-vote** | a flash-loan of the gov token → a snapshot-vote passes on the borrowed balance → repay |
| **the reward farm** | a deposit that earns a reward proportional to a briefly-inflated balance |
| **liquidation** | a skewed price triggers a liquidation the contract pays out on |

## The detection fingerprint

- a `flashLoan`/`borrow`/`flash` function that calls the borrower back
- a contract that reads `getPrice`/`reserve`/`balanceOf` for a value decision
- a decision that a temporary balance/price could skew
- **falsifier**: the price source is a TWAP/multi-block oracle (a same-tx skew
  doesn't move it), or no manipulable source feeds the decision

## The TWAP boundary

A time-weighted average price over several blocks resists a single-tx skew —
the loan repays within the block, the TWAP is unaffected. The bug is only a
contract that reads the SPOT/current-block value.

## The evidence

`cast call` the contract's balance/flag before/after; the flash-loan contract's
deploy + the atomic `attack()` tx (the receipt shows the loan + the calls +
the repay in one tx) + `isSolved() → true` are the chain.
