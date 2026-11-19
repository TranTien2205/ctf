# Edge cases deep — the boundary conditions that actually fire

`edge-cases.md` catalogues the values. This module is the physics — WHY
each boundary exists and which stacks expose it.

## The precision boundaries (JavaScript / JSON)

`Number` is IEEE-754 double: integers are exact only to 2^53.

```
9007199254740991   = MAX_SAFE_INTEGER  (exact)
9007199254740992   = MAX_SAFE + 1      (still exact)
9007199254740993   → stored as ...992  (precision loss begins)
```

A checker comparing `id <= 9007199254740993` and a sink using the value
see DIFFERENT numbers above the boundary — the classic float-precision
validator gap. `1e309` → `Infinity`; `Infinity < limit` is `false`,
`Infinity * price` is `Infinity` or `NaN`, and `NaN` comparisons are
all-false — every guard `x > 0` and `x < limit` passes `NaN` cleanly.

Node/Express bodies parse `"9007199254740993"` as the JSON number —
precision lost at parse, before the checker runs.

## The width boundaries (C-likes, databases, fixed-point)

| Width | Max | The wrap probe |
|---|---|---|
| int32 | 2,147,483,647 | `2147483648` → `-2147483648` on signed wrap |
| uint32 | 4,294,967,295 | `4294967296` → `0` |
| int64 | 9,223,372,036,854,775,807 | `9223372036854775808` |
| uint64 | 18,446,744,073,709,551,615 | `18446744073709551616` |
| uint8 | 255 | `256` → `0` |
| uint16 | 65,535 | `65536` → `0` |

Money in cents is often int32 — `2147483648` cents wraps to a negative
balance of the same magnitude. A `balance + price > limit` check in
int32 can wrap past its own ceiling: `INT_MAX - 1 + price` → negative,
which then passes `balance < limit` and underflows the account.

## The signedness boundary

`id` checked as unsigned but used in signed arithmetic (or vice versa):

- check: `id < LIMIT` with `id` unsigned → `id = 4294967295` fails.
- same `id` used signed → `-1` → `off + (-1)*S` → address BEFORE base.

The fix direction matters: `id >= 0` checked signed, `id` used unsigned —
negative inputs become huge positives at the sink.

## The transform boundary (the Pachinko shape)

`addr = off + id*S mod 2^w`. Boundaries:

- `id*S` overflowing `2^w` wraps — the wrap IS the reach: large `id`
  lands on small addresses.
- `S` even loses invertibility — reachable addresses are the congruence
  class `{off + id*S mod 2^w}` — count `2^w / gcd(S, 2^w)` targets.
- `off` attacker-influenced shifts the whole class.
- `S` negative indexes below the base.
- `id` checked `id < LIMIT` but the sink checks nothing → `id` in
  `[LIMIT, UINT_MAX]` reaches wherever `off + id*S` lands.

## The step-index boundaries

`step=N+1` on an N-step flow: does the router wrap (`step % N`), clamp,
or 500? `step=-1` and `step=0` on a 1-indexed flow reach the pre-first
state. Non-integer steps — `step=1.5`, `step=two`, `step=null` — exercise
the parser's coercion path, often a different check than the flow's.

## The locale/coercion boundaries

- `"1,000"` parses as 1 in `parseInt` (stops at `,`), as 1000 in some
  locale-aware parsers, as NaN in strict JSON.
- `+1`, `" 1"`, `"1 "` — whitespace/sign coercion differs by parser.
- `"01"` — leading zero → octal in some parsers, decimal in JSON.
- `1_000` — valid numeric literal in modern Python/JS source, invalid
  in `int()`/`Number()` calls.
- Unicode digits (`１２３` fullwidth) — normalized by some validators,
  rejected by parsers.

## The duplicate-key boundary

```
POST /op?role=user&role=admin          qs libraries: last, first, or array
{"role":"user","role":"admin"}         JSON: most parsers take LAST
role=user&Role=admin                   case-sensitive merge
```

The validator sees one value, the binder applies another — the same
structural gap as scaling-after-check, at the parse layer. If a
middleware validates `role=user` and the handler binds `role=admin`,
the check is bypassed with a duplicate key — probe both orders.

## The empty/boundary-collection cases

- `items=[]` — an empty cart checkout; does total computation 500 or
  confirm a zero order?
- `items=null` vs `items` absent — different code paths.
- `coupon=""` — empty-string coupon where null is checked.
- `roles=[]` — an empty array binding where `roles` expected a string —
  array-vs-scalar confusion in `in` checks (`"admin" in []` vs
  `[] == "admin"`).

## The clock boundaries

- `expiry == now` — `<=` vs `<` decides whether "expired now" is valid.
- uint32 epoch wrap: `2106-02-07` — `timestamp=4294967296` → `1970` again.
- int32 signed epoch: `2038-01-19T03:14:08Z` is the last second.
- DST gaps: `2024-03-10T02:30` doesn't exist in US timezones — does the
  parser reject, shift, or crash?
- `notBefore` future vs `expiry` past: a token valid in a window the
  comparison order might invert.
