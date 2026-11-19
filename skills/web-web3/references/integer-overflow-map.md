# Integer-overflow map — the wrap shapes indexed

## The version → the wrap viability

| The pragma | The wrap |
|---|---|
| `<0.5` | silent wrap — no SafeMath default |
| `^0.5-^0.7` | silent wrap unless `SafeMath`/`using SafeMath` on the path |
| `>=0.8` | REVERTS — unless inside `unchecked { }` |
| `>=0.8` + `unchecked` | deliberate wrap — the block is the bug |

## The operation → the shape

| The op | The wrap |
|---|---|
| `a - b`, `a < b` | underflow → `a - b` goes to `2**256 - (b - a)` |
| `a + b` | overflow → past `2**256-1` wraps to `(a+b) mod 2^256` |
| `a * b` | overflow → the product wraps |
| `a / b` | `b == 0` reverts regardless — the divide-by-zero |
| `counter++`/`counter += n` | a counter past its bound wraps |
| `int` (signed) | wraps at `2**255` |
| `array.length--` (pre-0.8) | underflows to `2**256-1` → the whole-storage array |

## The exploit-shape → the call

| The shape | The call |
|---|---|
| `balances[me] - amt` underflow | `transfer(1)` on `balances[me]=0` → `2**256-1` |
| `amount + fee <= limit` | `amount = 2**256 - fee + 1` → the sum wraps to ~0 |
| `v * count` batch | a `count` that overflows the product → mints each the full `v` |
| `supply + mint <= max` | `mint` wraps `supply` past `max` |
| `array.length--` | `retract()` underflows → `revise(i, v)` writes any slot |

## The accounting-integrity shape

Not a wrap — a desync: `total`/`totalShares`/`totalAssets` diverges from the
real sum — a path credits shares without debiting `total`, burns twice, or
rounds in the attacker's favour → `accounting-vault.md`.

## The falsifier map

| The falsifier | Closes |
|---|---|
| `>=0.8` pragma + no `unchecked` on the path | the wrap — arithmetic reverts |
| `SafeMath`/`using SafeMath` on the path | the wrap — SafeMath reverts |
| the path doesn't do the arithmetic | the class — no wrap point |

## The detection order

```bash
grep pragma Challenge.sol          # <0.8? >=0.8?
grep -n unchecked Challenge.sol    # the 0.8 deliberate-wrap
grep -n SafeMath Challenge.sol     # the guard — its absence on the path
```

`integer-overflow.md`/`integer-overflow-deep.md` for the full shapes.
