# Detection surface — where the logic-flaw signals appear in the transcript

## Response-body signals

| Signal | Mechanism it suggests |
|---|---|
| `{"role":"user","balance":0,"verified":false}` in a GET | mass assignment — fields exist the form doesn't send |
| `"total": 50` computed client-side then echoed | trust-in-earlier-step — a carried value |
| `"step": 1`, `"state": "cart"` in responses | workflow — steps exist to skip |
| `"code": "SAVE50"`, one-time tokens | replay/idempotency targets |
| `"id": 4096`-style indexes into shared structures | transform candidates |
| `"price": 100` next to `"unit": "cents"` | unit confusion |

## Request-shape signals

| Signal | Mechanism |
|---|---|
| hidden `<input type=hidden name=price>` | trust-in-earlier-step |
| `step=`/`state=` params or cookies | workflow skip |
| `Idempotency-Key` header | idempotency coverage |
| `qty`, `amount`, `discount`, `tax` fields | numeric boundary |
| `id`/`offset`/`index`/`page` fields | transform candidates |
| `objectId`/`docId`/`recordId` in operations | ownership |

## Code-shape signals (white-box)

| Source pattern | Mechanism |
|---|---|
| `Model.create(req.body)`, `Object.assign(user, req.body)` | mass assignment |
| `params.require(...).permit(...)`, `pick(body, [...])` | allowlist = falsifier |
| `if (!order)` before `order.status = 'confirmed'` | workflow skip |
| `if (qty === 0)` before `total += qty*price` | sign boundary |
| `findOne` → effect → `used = true` | replay window |
| `id < LIMIT` then `mem[off + id*S]` | scaling-after-check |
| `req.body.step`, `req.cookies.step` read by handlers | client-writable state |
| `total = req.body.total` | trust-in-earlier-step |

## Rejection-shape signals

| Rejection | Layer answering | Mechanism implication |
|---|---|---|
| `unknown field` | schema allowlist | mass assignment dead here |
| `must be positive` | field validator | boundary dead at this field |
| `302` to step 2 | state machine | ordering enforced — probe carriers |
| `already used` | idempotency store | serial replay dead — parallel is race |
| `price mismatch` | recomputation | trust dead at this value |
| `500` on out-of-limit index | transform/sink | the check missed the transform's output |

## Missing signals that are themselves signal

- NO `Idempotency-Key` handling on one-time actions → replay open.
- NO `permit`/`fillable`/`fields` near a `create` → binder unguarded.
- NO state param anywhere but multi-step UI → state may live only in
  the client flow — terminal endpoint bare-probe it.
- NO recompute at checkout (`total = req.body.total`) → trust gap.

Detection for logic flaws is as much about what's ABSENT in the
transcript as what's present — the checks that don't appear are the
edges the state machine permits.
