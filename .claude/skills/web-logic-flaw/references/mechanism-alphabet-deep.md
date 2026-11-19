# Mechanism alphabet deep — the full taxonomy with implementation reads

`mechanism-alphabet.md` is the overview. This module carries the code
level: for each mechanism, the vulnerable idiom, the safe idiom, and
the probe semantics.

## A — mass assignment

```js
// vulnerable
User.create(req.body)
// safe
User.create(pick(req.body, ['username','password']))
```

Probe semantics: the write-echo vs read-back diff. The binder's
allowlist is the mechanism; the falsifier is a stored-default on
read-back.

## B — workflow skip

```js
// vulnerable — pre() checks existence, not state
app.post('/confirm', async (req,res) => {
  const o = await Order.findById(req.body.orderId);
  if (!o) return 404;
  o.status = 'confirmed';
});
// safe — pre() checks the required predicate
if (o.status !== 'paid') return 400;
```

Probe semantics: the impossible pair — terminal field set, precondition
field unset.

## C — state replay

```js
// vulnerable — no consumed marker
app.post('/redeem', async (req,res) => {
  const c = await Code.findOne({code:req.body.code});
  user.balance += c.value; await user.save();
});
// safe — check-and-set, atomically
await Code.findOneAndUpdate({code, used:false}, {used:true});
```

Probe semantics: serial double-apply vs `409`; the marker's scope and
atomicity are the follow-on questions.

## D — numeric boundary

```js
// vulnerable — nonzero, not positive
if (qty === 0) return 400;
// safe
if (!Number.isSafeInteger(qty) || qty <= 0) return 400;
```

Probe semantics: the alphabet per field; each value exercises a
different guard path (sign, zero, type, NaN, width, coercion).

## E — scaling-after-check

```js
// vulnerable — check raw, use transformed
if (id >= LIMIT) return 400;
mem[off + id*S] = v;
// safe — bound the sink's address
const addr = off + id*S;
if (addr >= BOUND) return 400;
```

Probe semantics: the different-layer rejection; `id` values past the
documented bound compared against malformed-input rejections.

## F — unit confusion

```js
// vulnerable — implicit unit
const charge = req.body.price;         // 100 = dollars? cents?
// safe — explicit unit, canonical conversion
const chargeCents = toCents(req.body.price, req.body.unit);
```

Probe semantics: the same magnitude in both units; the stored/charged
value reveals which representation the sink used.

## G — role assignment

Mass assignment's privileged-field specialization — same idioms, higher
stakes reading.

## H — idempotency

```js
// vulnerable — key never consulted
// safe — atomic check-and-set on the key
await Idem.findOneAndUpdate({key, done:false}, {done:true});
```

Probe semantics: the key's coverage — same key mutated body, cross-user,
cross-endpoint, cross-object.

## I — time assumption

```js
// vulnerable — expiry trusted from client
if (token.expiry > Date.now()) ...
// with token.expiry client-controlled
// safe — server-issued expiry, server clock
```

Probe semantics: past/future values per time field; inclusive-vs-
exclusive boundary at `expiry == now`.

## J — sequence assumption

```js
// vulnerable — accepts any sequence value
if (req.body.nonce !== undefined) apply(...);
// safe — strictly increasing, tracked server-side
if (nonce <= lastSeen) return 409;
```

Probe semantics: stale/replayed/out-of-order IDs; `id=0`, `id=-1`,
`id=MAX` boundary forms.

## K — ownership assumption

```js
// vulnerable — transition path skips the owner check
app.post('/order/:id/confirm', ...);   // no order.userId check
// safe — owner check on every path touching the object
```

Probe semantics: foreign `objectId` through the TRANSITION path even
when the read path 403s.

## L — singleton assumption

```js
// vulnerable — uniqueness assumed, not enforced
// safe — unique constraint at the store
```

Probe semantics: a second create of "the" object; scope-variant names
(case, whitespace).

## M — trust-in-earlier-step

```js
// vulnerable — upstream value re-trusted downstream
const total = req.body.total;          // minted at step 1
charge(total);
// safe — recompute at the sink
const total = recompute(order); charge(total);
```

Probe semantics: minted-vs-accepted diff — `50` minted, `1` charged.

## The composite read

Real handlers mix mechanisms — `User.create(req.body)` inside a step
handler that also trusts `req.body.step`. The alphabet is orthogonal:
falsify each independently; a live composite is the chain.
