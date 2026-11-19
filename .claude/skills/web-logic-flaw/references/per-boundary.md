# Per-boundary map — each numeric boundary, what it breaks and where

Every entry in the boundary alphabet exists because some code path
treats it differently from its neighbors. This map names the code path
per boundary value.

## `-1`

- **Breaks**: `qty != 0` checks that meant `qty > 0`; totals that
  subtract into the negative; refund-shaped sinks.
- **Where it lands**: sign-less validation, `unsigned` coercion (becomes
  huge), arithmetic that assumes positive operands.
- **Read the response for**: negative total, refund, wrapped-huge value.

## `0`

- **Breaks**: "must be nonzero" workflows that forget it — free items,
  zero-price orders, division sites.
- **Where it lands**: `qty*price=0` → free; `amount/qty` → division;
  `id=0` → the first object / the "null" object.
- **Read for**: `total:0` confirming, `500` on division, the zeroth
  record returned.

## `-0`

- **Breaks**: `Object.is(-0, 0)` is `false` in JS — a check using
  `Object.is` or `SameValue` semantics distinguishes `-0` from `0` while
  arithmetic treats them alike.
- **Where it lands**: checks that "passed" `0` while the sink saw `-0`;
  signed-zero serialization differences.

## `0.1`, `0.0000001`, `1.0000000000000002`

- **Breaks**: integer-typed assumptions — `qty=0.1` where stock counts
  integers; floating-point `qty*price` precision.
- **Where it lands**: fractional orders, totals rounding up vs down,
  `0.1+0.2 != 0.3` comparisons that fail equality checks.

## `NaN`

- **Breaks**: ALL comparisons — `NaN > 0` false, `NaN < limit` false.
  A guard `if (qty > 0) ok else reject` rejects; a guard
  `if (qty <= 0) reject else ok` ACCEPTS. The guard's polarity decides.
- **Where it lands**: `total=NaN` propagating into confirmed orders;
  `isNaN()` absent in the validator.
- **Probe note**: JSON can't carry literal `NaN` — it arrives as the
  string `"NaN"` (parser coercion), a form value, or computed
  (`0/0`-shaped expressions where the server evaluates).

## `Infinity`, `1e309`, `-Infinity`

- **Breaks**: `total < balance` checks against `Infinity` totals fail
  open or closed depending on polarity; `Infinity` in a sum is
  `Infinity`; `Infinity - Infinity` is `NaN`.
- **Where it lands**: overflow-prone totals, `limit` comparisons,
  serialization (`Infinity` unserializable in JSON — a `500` at the
  serializer is itself signal).

## `2147483647` / `2147483648` (int32 edge)

- **Breaks**: signed int32 storage — `MAX+1` wraps to `INT32_MIN`; money
  in cents overflowing the field width.
- **Where it lands**: `balance + amount` checks that overflow past the
  ceiling into negative; `qty*price` computed in int32.
- **Read for**: a huge positive becoming a huge negative — the wrap is
  the verbatim evidence.

## `4294967295` / `4294967296` (uint32 edge)

- **Breaks**: unsigned storage — `4294967296` → `0`; `id` fields
  stored uint32 while the checker used wider math.
- **Where it lands**: ID transforms, timestamps, record counts.

## `9007199254740991` / `9007199254740992` / `9007199254740993`

- **Breaks**: JS/JSON `Number` precision — `...993` unrepresentable,
  becomes `...992` at parse. The checker compares the parsed value;
  the request carried a different integer.
- **Where it lands**: any `id`/`amount` parsed as JSON number — the
  parse-time precision loss is a validator gap that exists before the
  code runs.

## `0x10`, `0o10`, `0b1010`, `010`, `08`, `09`

- **Breaks**: radix assumptions — `parseInt("0x10")` → 16 where
  `Number` semantics differ; `010` octal in sloppy parsers, decimal in
  strict ones; `08`/`09` invalid-octal edge cases.
- **Where it lands**: `parseInt` without radix, `int(x, 0)` Python
  auto-radix, loose `strconv` paths.

## `"1"`, `[]`, `{}`, `null`, `true`

- **Breaks**: type coercion — `"1" == 1` loose-true; `[]` falsy-but-
  present; `null` skipping `!= null` guards; `true` coercing to `1`.
- **Where it lands**: `==` vs `===` checks, `empty()` semantics,
  array-vs-scalar confusion, truthiness guards.

## Locale/separator forms — `1,000`, `1 000`, `1_000`, `1.000,00`

- **Breaks**: `parseInt("1,000")` → 1 (stops at comma) where
  locale-aware parsers read 1000; `_` valid in source literals, invalid
  in `int()`.
- **Where it lands**: string→number coercion paths that differ between
  validator and sink — the same structural gap as scaling-after-check,
  at the parse layer.

## Reading the result

Each boundary's verdict:

| Result | Layer | Next |
|---|---|---|
| `400` | field validator | next FIELD, not next spelling |
| `200` + clamp | silent bound | boundary dead, note the clamp |
| `200` + forbidden state | arithmetic unguarded | CONFIRM → chain to checkout |
| `500`/crash | unguarded transform/sink | CONFIRM — different-layer signal |
