# Accounting / vault / token logic — lie about the balance

## The shape

A contract that tracks deposits/shares/balances and pays out on the tracked
value — a `vault`, `bank`, `staking`, or token contract. The bug is a path that
desyncs the tracked number from the real one.

```solidity
function deposit() payable { shares[msg.sender] += msg.value * rate; }
function withdraw(uint s) { payable(msg.sender).transfer(s / rate); }
// a rate that a path can skew → withdraw pays more than deposited
```

## The bug classes

| Bug | The shape |
|---|---|
| **share-price manipulation** | a donation/transfer directly to the contract (not via `deposit`) inflates the backing → `deposit` mints shares at a skewed price, or the first-depositor rounding lets an attacker steal the next deposit |
| **double-claim** | a `withdraw`/`claim` that doesn't zero the claim first, or a mapping read that a reentrancy resets |
| **wrong rate** | `s / rate` where `rate` a path can change |
| **fee/reward desync** | the reward math credits more than the contract holds |
| **flash-loan skew** | a borrowed sum that briefly inflates a balance the contract reads for the decision — return the loan in the same tx, keep the skewed payout |
| **ERC-20 decimals** | a `decimals` mismatch between the token and the vault's assumption |
| **approval/transferFrom** | an `approve` left open, or a `transferFrom` that doesn't check allowance |

## The first-depositor attack

The classic vault inflation: attacker deposits `1 wei` → minted `1 share`; then
transfers `X` directly to the vault (no shares minted); the next depositor's
`deposit` computes `amount * totalShares / totalAssets` = `amount * 1 / (1+X)`
→ rounds to `0` shares — the attacker (holding all the shares) owns the whole
backing.

## The flash-loan shape

```solidity
loan(amount):   // borrow, use, repay — all in one tx
    vault.deposit{value: amount}();       // huge temporary deposit
    skewedAction();                       // the contract reads the inflated balance
    vault.withdraw();                     // take it back
    repay loan + fee                      // keep the skewed payout
```

The loan is repaid atomically — the only cost is the fee; the payout is the
contract's real balance drained by the lie.

## The detection fingerprint

- a `deposit`/`withdraw`/`claim`/`stake`/`redeem`/`borrow` pair
- a `rate`/`totalShares`/`totalAssets`/`exchangeRate` computed from a manipulable balance
- **falsifier**: the tracked value can't be desynced — every in/out path updates
  it atomically and no donation/reentrancy path bypasses it

## The evidence

`cast call` the tracked balance and the real `cast balance` before/after —
the desync and the drained amount are the proof.
