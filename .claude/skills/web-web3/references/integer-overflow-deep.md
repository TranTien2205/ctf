# Integer overflow / underflow (deep) — every arithmetic-warp shape

## The version boundary

- `pragma <0.8` — arithmetic WRAPS silently (the SafeMath era). `0 - 1` →
  `2**256 - 1`, `2**255 + 2**255` → `0`.
- `pragma >=0.8` — the compiler inserts checks; over/underflow REVERTS. The bug
  then needs an `unchecked { }` block around the path.
- `SafeMath` on `<0.8` — the library re-adds the checks; its presence on the
  path falsifies the wrap.

## The detection fingerprint

```bash
grep pragma Challenge.sol          # <0.8 = wrap; >=0.8 needs unchecked
grep -n unchecked Challenge.sol    # the deliberate-wrap block
grep -n SafeMath Challenge.sol     # the guard — its absence on a path matters
```

The wrap is per-path — a contract can `SafeMath` most arithmetic but leave one
`unchecked` or one pre-SafeMath expression.

## The shapes

### Underflow → huge balance

```solidity
balances[me] -= amount;             // balances[me]=0, amount=1 → 2**256-1
```

A subtraction that goes negative wraps to a near-max value — the account ends
with an enormous balance → drain the contract.

### Overflow → bypass a cap / mint infinite

```solidity
require(amount + fee <= limit);
amount = type(uint256).max - fee + 1   →   amount + fee wraps to ~0 → passes
```

A `total`/sum/`amount + fee` that wraps to a small value defeats a `<=` cap.

### The batch-overflow (BEC)

```solidity
uint total = v * to.length;            // overflow → small total
require(balance >= total);             // passes on the wrapped total
for (to) balances[to[i]] += v;         // each recipient gets the FULL v
```

The product `v * count` overflows to a small number the `require` accepts, but
the per-recipient credit is the full `v` — mint huge value.

### The counter wrap

A `count`/`nonce`/`supply` that overflows past a bound — `supply` wraps past
`maxSupply` and keeps minting; a `nonce` wraps and replays.

## The account-integrity variant

Not a wrap — a wrong invariant: `totalShares`/`totalAssets`/`total` desyncs from
the real sum. A path that credits shares without debiting `total`, burns twice,
or lets a donation inflate the backing → a withdraw that pays more than the
share should.

## The 0.8 `unchecked` hunt

On a `>=0.8` contract, grep `unchecked` — the arithmetic inside it wraps. A
challenge whose bug is a wrap on a `>=0.8` pragma puts it inside `unchecked`;
the `unchecked` block IS the detection signal.

## The evidence

`cast call` the balance/var before/after — the wrapped value (`0 → 2**256-1`)
is the proof. A drain's `cast balance $CH` → 0 is the impact.
