# Accounting / vault (deep) — every balance-desync shape

## The invariant that breaks

A vault/bank/staking tracks `shares`/`balances`/`totalAssets` and pays out on
the tracked value. The bug is a path that desyncs tracked-from-real:

```solidity
deposit():      shares[me] += amount * rate;      totalAssets += amount;
withdraw(s):    pay(s * totalAssets / totalShares);
```

`pay` divides by `totalShares` — a path that inflates `totalAssets` without
minting shares, or mints shares without crediting `totalAssets`, breaks the
rate.

## The first-depositor attack

```solidity
// attacker deposits 1 wei → minted 1 share (totalAssets=1, totalShares=1)
// attacker transfers X directly to the vault (no shares) → totalAssets=1+X
// victim deposits amount → shares = amount*totalShares/totalAssets
//                          = amount*1/(1+X) → rounds to 0 shares
// attacker (holding the only share) owns all the backing
```

The rounding `amount * totalShares / totalAssets` → `0` on a big enough
donation — the first-depositor holds all shares → `redeem` drains the vault.

## The donation-inflation shape

A direct `transfer`/`send`/`selfdestruct` force-feed to the vault inflates
`totalAssets`/`balance` without minting shares → the share-price jumps → the
attacker's shares are worth more, or the next deposit gets 0 shares.

## The double-claim / reentrancy-accounting

A `withdraw`/`claim` that credits before settling — the reentrancy drains the
tracked balance, or the claim doesn't zero so it's claimed twice. The same
`call`-before-update bug, measured in the accounting desync.

## The rate/rounding shape

`s / rate` where `rate` a path can change; a division that rounds in the
attacker's favour (`mulDiv` direction); a fee that credits the fee-collector
in a loop the attacker triggers.

## The flash-loan-skew shape

```solidity
loan(amount):
    deposit{value: amount}()        // temporary huge deposit
    the contract reads the inflated balance for the decision
    withdraw()                      // take it back
    repay(amount + fee)             // keep the skewed payout
```

The loan is repaid atomically — the cost is the fee; the payout is the desynced
share of the real backing.

## The ERC-4626 vault surface

A `deposit`/`mint`/`withdraw`/`redeem` on a standard vault — the
`convertToShares`/`convertToAssets` math is the surface. The rounding direction,
the `totalAssets` source (a manipulable balance vs an internal accounting),
and the donation inflation are the bugs.

## The detection fingerprint

- `deposit`/`withdraw`/`stake`/`redeem`/`mint`/`burn`/`claim`/`borrow`
- `totalShares`/`totalAssets`/`rate`/`exchangeRate`/`getPricePerShare`
- a `transfer`-to-the-contract path (the donation surface)
- **falsifier**: every in/out path updates the tracked value atomically; no
  donation/reentrancy/flash path desyncs it

## The evidence

`cast call` `totalAssets`/`totalShares`/`balanceOf` + `cast balance` the real
balance before/after — the desync and the drained amount are the proof.
