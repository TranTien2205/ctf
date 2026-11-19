# Numeric boundary — the type permits values the rule forbids

The type permits `-1`, `0`, `999999999`, `0.0000001`, `NaN`, `Infinity` —
the rule forbids them. The handler trusts the type (int, float, JSON
number), not the domain (positive, bounded, sane).

## The mechanism

```
POST /cart  {"productId": 2, "quantity": -1}
                                      ^^ the type permits it — the rule forbids it
```

The handler computes `price * quantity` and charges the result — a
negative total, a zero charge, a wrapped total.

## The detection

### The arithmetic sinks

Every place a request value enters arithmetic:

- `total = price * quantity` — quantity negative → total negative.
- `balance = balance - amount` — amount > balance → negative balance.
- `price = base * discount` — discount > 1 → negative price.
- `total = sum(items)` — a huge item → overflow.
- `offset = index * stride` — index huge → wrap or out-of-range.
- `address = base + index * scale` — the Pachinko shape: index checked
  pre-scaling, scaled address out of range or wrapped.

### The value dictionary

| Value | The surface | The payoff |
|---|---|---|
| `-1` | quantity, amount, count | negative total → refund, or negative balance |
| `0` | quantity, price, count | free — zero total |
| `0.0` / `0.0000001` | float fields | rounds to zero or sub-unit |
| `999999999` | quantity, amount | overflow — wraps to low value |
| `2147483647` (`INT_MAX`) | int32 fields | +1 wraps to `INT_MIN` |
| `4294967295` (`UINT_MAX`) | uint32 fields | +1 wraps to `0` |
| `18446744073709551615` (`UINT64_MAX`) | uint64 fields | wrap |
| `NaN` | float fields | comparisons all false — checks pass |
| `Infinity` / `-Infinity` | float fields | comparisons true/false — checks bypassed |
| `1e308` | JSON number | parses to `Infinity` |
| `-0` | signed zero | `x === 0` true but `1/x` is `-Infinity` |
| `0.1 + 0.2` arithmetic | float rounding | `0.30000000000000004` — equality fails |
| `+1`, ` 1`, `1.0`, `1e0` | type coercion | different parses of the same value |
| `%` encoded digits | parser differentials | `1%30` parses as `1` |
| `0x10` | hex parsing | `16` in some parsers, `0` or error in others |
| `1,000` | locale parsing | `1` or `1000` or error |

## The probe

```bash
# the forbidden value — one at a time
curl -i -b "$JAR" -X POST "$BASE/cart" -d 'productId=2&quantity=-1'

# read the state back — the cart, the total, the balance
curl -i -b "$JAR" "$BASE/cart"
curl -i -b "$JAR" "$BASE/checkout" -X POST
```

## The confirmation

The state the rules forbid is reached:

```
HTTP/1.1 200 OK
{"cart": [{"productId": 2, "quantity": -1, "price": 50}],
 "total": -50, "charged": -50}
```

A negative total charged — the account's balance increased by purchasing.
Or:

```
{"total": 0, "charged": 0, "items": [{"productId": 2, "quantity": 0}]}
```

A zero charge for real items — the goods ship free.

## The falsifier

The handler validates the domain — the response names the violation:

```
HTTP/1.1 400 Bad Request
{"error": "quantity must be positive"}
```

or the value is silently clamped to the domain — the response shows the
clamped value, not the sent one:

```
{"quantity": 1, "total": 50}
```

The silently-corrected value is a negative — the check ran, record it.

## The arithmetic shapes

### Negative quantity → refund

```
cart: [{productId: 2, qty: -1, price: 50}] → total: -50
charge of -50 → credit of 50 to the account
```

### Zero price → free

```
cart: [{productId: 2, qty: 1, price: 0}] → total: 0
goods ship, nothing charged
```

### Integer overflow → wrap

```
price: 100, qty: 21474836 (INT_MAX/100+1)
total = price * qty → wraps to a small or negative value
```

### Float rounding → sub-unit

```
price: 0.10, qty: 0.0000001
total: 0.00000001 → rounds to 0 at charge time
```

### Discount > 100% → negative

```
discount: 1.5 (150% off)
price: 100, final: -50
```

### The scaling-after-check (Pachinko)

```
index checked: index < 0x1000
transformed: addr = (index ^ 0xffff) * scale + base
index = 0xfff → transformed addr wraps into instruction memory
```

The check ran on the pre-transform value; the transform produced an
out-of-range or wrapped address. The check's domain and the address's
domain disagree.

## The evidence rules

- The forbidden state must be verbatim in the response — `total: -50`,
  `charged: -50`, `balance: 1000050`.
- A `200` with the clamped value is a negative — the check ran.
- A `500` is a crash, not a confirmation — the arithmetic broke but nothing
  proves the forbidden state was stored.
- Read the state back through the normal view — the cart, the balance, the
  order — not the error page.

## The traps

- **The type-check is not the domain-check.** `typeof quantity === 'number'`
  accepts `-1`; `quantity > 0` is a separate check.
- **Float equality fails.** `0.1 + 0.2 !== 0.3` — a check like
  `total === expected` may fail on floats, or pass on a crafted one.
- **`NaN` poisons comparisons.** `NaN > 0`, `NaN < 0`, `NaN === NaN` are all
  false — a `NaN` in a comparison chain can bypass bounds checks.
- **Integer width differs by layer.** JS numbers are doubles (53-bit);
  Python ints are unbounded; Go ints are platform-sized. A value that
  overflows Go's int32 does not overflow JS's double — and vice versa.
