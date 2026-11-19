# Numeric boundary deep — the arithmetic internals per value class

`numeric-boundary.md` covers the alphabet. This module is the physics —
what each value does inside the arithmetic, per stack.

## The NaN semantics (JS and IEEE everywhere)

```
NaN > 0     → false        NaN < limit  → false
NaN === NaN → false        NaN * price  → NaN
if (qty > 0)              → false → falls to reject
if (qty <= 0) reject      → false → falls to accept
```

Guard polarity decides: `if (!(qty > 0))` rejects NaN; `if (qty <= 0)`
accepts it. In source, read the polarity; black-box, `NaN` is a two-
outcome probe — `400` means the guard was `!(x>0)`-shaped; `200` means
`x<=0`-shaped — and a `NaN` total propagating into a confirmed order is
the verbatim evidence.

JSON can't carry literal `NaN` — it arrives as a string `"NaN"` that
loose coercion (`Number("NaN")`) produces, a form field, or a computed
expression. `null` parses to `null` not `NaN`; `Number(null)` is `0` —
different values, different probes.

## The Infinity semantics

```
Infinity * 0        → NaN
Infinity - Infinity → NaN
Infinity > limit    → true    Infinity < balance → false
```

`qty=Infinity` → `total=Infinity` → `total > balance` is `true` →
rejected by `>`-shaped balance checks, ACCEPTED by `total <= balance`
checks missing (or `balance` itself Infinity). `-Infinity` totals pass
`<`-shaped checks into negative territory. JSON serialization of
`Infinity` → `null` or throws — a `500` on the write response is
itself layer-locating signal.

## The wrap semantics (int widths)

```
INT32:   2147483647 + 1 → -2147483648
UINT32:  4294967295 + 1 → 0
INT64:   9223372036854775807 + 1 → -9223372036854775808
```

Where the wrap matters in logic terms:

- `balance + amount > MAX` — a deposit that wraps balance negative
  passes `balance < limit` checks.
- `qty * price` computed in int32 — `qty=50000, price=50000` →
  `2.5e9 > INT32_MAX` → wraps negative → free order.
- counters/indexes `id` stored int32, computed int64 — the checker
  compares int64, the store wraps int32.

## The precision semantics (2^53)

```
JSON: 9007199254740993 → parsed 9007199254740992
```

The request carries one integer; the checker compares another. Any
`id`/`amount`/`balance` parsed as a JSON number above 2^53 has this
gap — the checker's `id <= N` may pass `id` values that became `id+1`
at parse.

## The coercion semantics (string→number)

| Stack | `"0x10"` | `"010"` | `"1e3"` | `"NaN"` | `""` | `" 1"` | `"1,000"` |
|---|---|---|---|---|---|---|---|
| JS `Number` | 16 | 10 | 1000 | NaN | 0 | 1 | NaN |
| JS `parseInt` | 16* | 10* | 1 | NaN | NaN | 1 | 1 |
| py `int()` | err | 10 | err | err | err | 1 | err |
| py `float()` | err | 10.0 | 1000.0 | nan | err | 1.0 | err |
| PHP `(int)` | 0 | 10 | 1000 | 0 | 0 | 1 | 1 |
| Go `strconv.Atoi` | err | 10 | err | err | err | err | err |

*radix-dependent. The CHECKER's coercion and the SINK's may differ —
`parseInt(qty)` in the validator, `qty*price` raw in the total: the
string `"0x10"` validates as 16 but multiplies as `"0x10"*price → NaN`
in sloppy code, or 16*price where coercion is consistent.

## The sign semantics (where -1 becomes huge)

`id` checked `id >= 0` signed but stored unsigned: `-1` → `4294967295`.
Or checked unsigned `id < LIMIT` but used signed: `4294967295` → `-1`
→ `off + (-1)*S` → address before base. Signedness is a transform —
the checker's domain and the sink's differ, the Pachinko shape at one
bit's depth.

## The money semantics (cents vs dollars)

```
$1.00 stored as 100 (cents, int) vs 1.00 (dollars, float)
price=100 → charge $100.00 or $1.00
0.1 + 0.2 ≠ 0.3 → totals drifting a cent per op
```

Unit confusion is a boundary issue: the sink's unit vs the checker's.
`price=100` where the UI shows `$1.00` and the ledger stores cents —
charge `100` cents or `100` dollars depending which representation
`price` lands on.

## Reading the arithmetic for evidence

The verbatim evidence for a boundary confirm is the FORBIDDEN ARITHMETIC
STATE:

- `total: -50` — negative where positive required
- `total: NaN` + `status: confirmed` — NaN propagated
- `balance: 4294967295` — wrapped where bounded
- `charged: 0` + `items: [n]` — free where priced

The value alone is surface; the impossible combination is the class.
