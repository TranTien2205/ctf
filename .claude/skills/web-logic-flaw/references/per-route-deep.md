# Per-route deep — the endpoint internals behind each mechanism

`per-route.md` mapped mechanisms to endpoint shapes. This module reads
the handlers — what each route class's code looks like and where its
check lives.

## `/register` internals

```js
app.post('/register', async (req, res) => {
  const user = await User.create(req.body);          // merge-all
  res.json({id: user.id, role: user.role});
});
```

The whole question is `User.create`'s binder. Probe set: `role`,
`balance`, `verified`, `permissions` — then the nested and array
paths. The register endpoint's answer decides the whole class's first
probe result.

## `/cart` internals

```js
app.post('/cart', async (req, res) => {
  const {productId, quantity} = req.body;
  if (quantity === 0) return res.status(400).end();  // sign unchecked
  cart.items.push({productId, quantity});
});
```

`quantity === 0` rejects zero, passes `-1`, `NaN` (≠), `0.1`. The
cart-write handler is where the boundary alphabet earns its keep.

## `/checkout` internals

```js
app.post('/checkout', async (req, res) => {
  const total = cart.items.reduce((s,i) => s + i.qty*i.price, 0);
  if (total > user.balance) return res.status(402).end();
  user.balance -= total;                                // -50 → +50
  order.status = 'confirmed';
});
```

`balance -= (-50)` is `balance += 50` — the negative total credits the
account. The checkout is the boundary's sink: the cart's forbidden
state only matters if it survives here — probe `/checkout` after the
cart confirm.

## `/confirm` internals

```js
app.post('/confirm', async (req, res) => {
  const order = await Order.findById(req.body.orderId);
  if (!order) return res.status(404).end();
  order.status = 'confirmed';                         // no paid check
});
```

Existence-only `pre()` — the workflow-skip canonical site. The `orderId`
param adds the ownership variant: does `/confirm` check `order.userId
== req.user.id`? (if not, foreign-order confirmation — the IDOR-adjacent
logic edge).

## `/redeem` internals

```js
app.post('/redeem', async (req, res) => {
  const code = await Code.findOne({code: req.body.code});
  if (!code || code.used) return res.status(409).end();
  user.balance += code.value; await user.save();
  code.used = true; await code.save();                // after the effect
});
```

The `used` marker exists — check-then-set, non-atomic. Serial replay
falsifies ONLY if `used` is actually written; the write happening
AFTER `user.save()` opens the parallel window (race's ground). If
`code.used = true` is absent entirely — the serial shape, pure.

## `/transfer` internals

```js
app.post('/transfer', async (req, res) => {
  const {from, to, amount} = req.body;
  const src = await User.findById(from);
  if (src.balance < amount) return res.status(402).end();
  src.balance -= amount; await src.save();            // ← window
  const dst = await User.findById(to);
  dst.balance += amount; await dst.save();
});
```

Three independent gaps: `from` ownership (can you name another user's
account?), `amount` sign (negative transfer = inverse flow), `from==to`
(same-account net-zero that the balance check still approves).

## `/admin` internals

```js
app.get('/admin', requireRole('admin'), async (req, res) => {
  res.json({users: await User.find(), flag: process.env.FLAG});
});
```

The sink — reached through the role edge, not its own bug. The probe is
the GET after the role confirm; the flag is usually a field inside this
view (`flag` in `process.env`, a DB config row, an exported file).

## `/flag` internals

```js
app.get('/flag', async (req, res) => {
  if (!req.session.completed) return res.status(403).end();
  res.send(process.env.FLAG);
});
```

Checks a session bit — set by WHICH transition? The chain ends where
that bit flips: skipped-step confirm, purchased-flag-item, admin-view
render. The bare GET is the zero-cost probe — run it first, always.

## `/update`/`PATCH` internals

```js
app.patch('/users/me', async (req, res) => {
  Object.assign(req.user, req.body);                  // second binder
  await req.user.save();
});
```

A second binder on the same model — the register allowlist doesn't
apply here. `role` may bind on update where create rejected it. One
probe per method: `PATCH`, `PUT`, method-override `_method=PUT`.
