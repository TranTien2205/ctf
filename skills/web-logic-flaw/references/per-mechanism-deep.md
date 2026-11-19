# Per-mechanism deep — the implementation physics of each mechanism

`per-mechanism.md` gives probe/falsifier pairs. This module is the
implementation layer — what the code looks like, why it breaks, and the
exact probe mechanics per stack.

## mass assignment — the binder internals

```js
// Express/Mongoose — merge-all
const user = await User.create(req.body);
// or
Object.assign(user, req.body); await user.save();
```

```python
# Flask/SQLAlchemy — merge-all
user = User(**request.json)
# Django — allowlisted by ModelForm (falsifier lives here)
form = UserForm(request.POST)   # Meta.fields is the allowlist
```

```php
// Laravel — $fillable is the allowlist; its absence is the bug
$user = User::create($request->all());
```

```ruby
# Rails — strong params are the allowlist
User.create(params[:user])                    # old Rails / no permit: BUG
User.create(params.require(:user).permit(:u,:p))  # allowed
```

The probe must read the DIFF between the write's echo and a fresh GET —
frameworks echo `req.body` fields they never persisted.

## workflow skip — the state-machine internals

```js
// the weak check — order exists, not order paid
app.post('/confirm', async (req, res) => {
  const order = await Order.findById(req.body.orderId);
  if (!order) return res.status(404).end();
  order.status = 'confirmed';                   // no paid check
  await order.save();
});
```

The skip succeeds because `pre(confirm)` as coded is `order != null`;
the workflow requires `order.paid == true`. The verbatim proof pair is
`status:confirmed` + `paid:false`.

## state replay — the missing marker

```js
app.post('/redeem', async (req, res) => {
  const code = await Code.findOne({code: req.body.code});
  if (!code || code.used) return res.status(409).end();
  user.balance += code.value;
  await user.save();
  code.used = true; await code.save();          // set AFTER effect
});
```

Two gaps live here: the check-effect window (race) and — when `used` is
never set at all — the serial replay. Serial first: if `used` is never
written, the second POST passes `!code.used` identically.

## numeric boundary — the arithmetic internals

```js
// only checks nonzero — sign unchecked
if (qty === 0) return res.status(400).end();
total += qty * price;        // qty=-1 → total -= price
```

```python
# NaN slips through comparisons
if qty <= 0:                 # NaN <= 0 is False → falls through to "ok"
    abort(400)
total += qty * price
```

The guard's polarity decides NaN: `if not (qty > 0)` rejects NaN;
`if qty <= 0` accepts it. Read the source for the polarity; black-box,
probe `NaN` on both field shapes.

## scaling-after-check — the transform internals

```js
// the Pachinko shape, generalized
if (id >= LIMIT) return res.status(400).end();
const addr = off + id * STRIDE;
mem[addr] = value;           // addr may exceed the checked region
```

When `off + id*STRIDE` is computed in a `2^w` word (WASM linear memory,
fixed-width index), large-but-accepted `id` wraps into regions the
check never considered — including code space when data and
instructions share memory.

## unit confusion — the conversion internals

```js
// client sends dollars, ledger stores cents — or vice versa
const price = req.body.price;            // 100
const chargeCents = price * 100;         // intended: 1.00 → 100
```

The gap is a transform (`* 100` or `/ 100`) applied to one
representation while another representation flows through. Probe both
unit conventions; `100` charged as `100.00` vs `1.00` tells which side
of the conversion the value landed on.

## idempotency — the dedup-key internals

The key's coverage IS the mechanism:

```js
await Idem.findOne({key: req.get('Idempotency-Key'), user: req.user.id});
```

- key covers `(key,user)` → cross-user replay opens.
- key covers `(key)` → same key+mutated body answers "first-write-wins?"
- no key at all → serial replay, the pure shape.

## trust-in-earlier-step — the carried-value internals

```js
// minted at step 1, trusted at step 3
const total = req.body.total;            // was rendered from server calc
charge(card, total);
```

The minted value travels a client-writable carrier (hidden field, JSON
echo, cookie). The check that should exist — `recompute(total) ==
req.body.total` — is absent. Evidence: minted `50` vs accepted `1`.
