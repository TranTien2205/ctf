# Per-check deep — the check internals and the edge each one opens

`per-check.md` tabulated checks vs gaps. This module reads the check
implementations — the code idioms that produce each gap.

## "Object exists" — the findOne idiom

```js
const order = await Order.findById(id);
if (!order) return 404;
order.status = 'confirmed';               // transition without state pre()
```

The check asserts `order != null` — existence. The workflow requires
`order.status == 'paid'` — a state predicate. The gap is always visible
in the diff between the check line and the mutation line: when no
predicate on `order`'s fields stands between them, the transition is
state-blind.

Probe: call the transition on an object in the WRONG state (fresh cart,
unpaid order). Verbatim evidence: terminal field set + precondition
field unset.

## "Field well-formed" — the type-check idiom

```js
if (typeof qty !== 'number') return 400;
total += qty * price;
```

`typeof` asserts representation, not range. `-1`, `NaN`, `Infinity`
are all `'number'`. The validator's question ("is it a number?") is
weaker than the arithmetic's requirement ("is it a positive finite
integer?").

```python
if qty <= 0:            # NaN <= 0 → False — the NaN gap is polarity
    abort(400)
```

Guard polarity: `if not (x > 0)` vs `if x <= 0` — identical for normal
numbers, OPPOSITE for `NaN`. Read the source; black-box, probe `NaN`.

## "Allowlisted" — the pick idiom

```js
const fields = pick(req.body, ['username', 'password']);
User.create(fields);
```

Closes flat extras. Open questions:

- is the allowlist recursive? `pick` is shallow —
  `{"profile":{"role":...}}` passes if `profile` is allowed;
- does another method share the model? the `PATCH` may not pick;
- does the schema validate or just pick? `additionalProperties:true`
  passes extras into `req.body` where merge-all codepaths may bind them.

## "Precondition ran" — the flag idiom

```js
if (req.session.step < 3) return redirect('/step2');
```

Where `req.session` is: server-side (real) vs cookie-session
(`req.cookies.step`, forgeable if unsigned) vs `req.body.step`
(attacker-supplied entirely — the check reads YOUR claim).

```js
if (order.paid) ship(order);
```

checked at step 3 — but `paid` was set by a step-2 handler whose OWN
precondition (a payment webhook) is itself a trust-in-earlier-step
candidate.

## "Uniqueness" — the constraint idiom

```js
User.create({username});          // unique index on username only
```

Unique on `username` ≠ unique on `role`, `email` (case variants
`Admin@x`), or the singleton object. The constraint's COLUMN coverage
is the mechanism boundary.

## "Idempotent" — the key idiom

```js
if (await Idem.findOne({key, user})) return 409;
```

The key covers `(key,user)`. Uncovered dimensions: same key+mutated
body (does the store hash the body?), cross-endpoint (the key store is
per-route?), cross-object (key scoped to the action or the resource?).

## "Owner" — the ownership idiom

```js
if (order.userId !== req.user.id) return 403;
```

On the READ path — but the transition path (`POST /order/:id/confirm`)
may not repeat it. Read-path and transition-path checks are separate
layers; probe the transition on the foreign object even when the read
403s.

## The composite: checks that check the wrong copy

```js
if (req.body.price <= MAX) process(order, computedPrice);
```

`req.body.price` checked; `computedPrice` charged — two different
values under one check. This is the generalized Pachinko: **the checked
value is not the used value**. Every check audit ends with the same
question — does anything transform, recompute, or re-source the value
between the check line and the use line?
