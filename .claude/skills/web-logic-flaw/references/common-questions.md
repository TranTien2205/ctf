# Common questions — business-logic testing, answered

## "When do I open this skill?"

After `classify.py` names `web-logic-flaw`, or when the observation is "a
multi-step flow / a numeric field / a register endpoint / a one-time
action" and no injection-class signal dominates. Also when `chain_match`
returns the Pachinko card's *shape* — a checked value transformed before
use.

## "Isn't this just mass assignment?"

Mass assignment is ONE mechanism in the alphabet — the field-binding
shape. Workflow skips, replays, boundaries, transforms, and trust gaps
are also logic flaws and have nothing to do with field binding. If your
confirmed bug is `role=admin` at register, file it under
`web-mass-assignment` (the dedicated class) — see `class-boundary.md`.

## "How is this different from IDOR?"

IDOR is *object access* — another user's `objectId` returns their data.
Logic-flaw is *state transition* — the workflow lets the object's state
move illegally. `GET /order/999` → IDOR. `POST /confirm` on an unpaid
order → logic-flaw. `POST /confirm` on *another user's* order → arguably
both; the verbatim evidence decides which class to record.

## "Serial replay or race?"

Serial replay first, always. A redeem that succeeds twice serially is a
missing-dedup logic flaw — no threads needed. Only when serial replay is
blocked (`409` on the second) does the parallel window become interesting
— that's `web-race-condition`, and `race_probe`'s serial baseline exists
for exactly this ordering.

## "The form only has username/password — where do I find the fields?"

The form is not the model. Find the fields in:

- the API's own GET responses (`GET /api/user/me` returns every field
  the model carries — including `role`),
- the front-end bundle (`bundle_miner` — the JS often builds a
  `{"role": ...}` object the form never renders),
- error messages (`"role must be one of: user, admin"`),
- other endpoints (an admin panel's update form exposes the field names).

## "What if the field gets rejected with 400?"

`400 unknown field` is the strict-schema falsifier — the binder layer is
closed. But ONE field's rejection doesn't close mass assignment: the
allowlist may cover `role` while `verified` binds fine. Still — after a
few `400`s, assume strict schema and change MECHANISM, not field
spelling.

## "How do I prove a negative price matters?"

`total: -50` on the cart response is the class confirm. The impact
confirm is the *checkout accepting it*: `POST /checkout` →
`"charged": -50` or `"refunded": 50`. A negative cart nobody can check
out is a curiosity, not an exploit.

## "What's the wrap math for the Pachinko shape?"

Given `addr = off + id*S mod 2^w` and a target address T:

```
id ≡ (T - off) * S^{-1}   (mod 2^w)        — when S is odd (invertible)
```

For even S, `id` exists only when `(T - off)` is divisible by
`gcd(S, 2^w)` — solve `id = (T-off)/gcd * (S/gcd)^{-1} mod 2^w/gcd`.
Pick the `id` in the checker's *accepted* range that lands on T.

## "The app validates everything — is logic-flaw dead?"

Field validation being tight says nothing about ordering, replay, or
trust. The alphabet is independent axes: an app can allowlist every
field AND still let `/confirm` run without `/pay`. Falsify mechanisms,
not fields.

## "How many probes is enough?"

`decide.py` enforces it: five probes or fifteen minutes per mechanism
class, twenty-five or forty-five for the challenge. A falsifier firing
counts toward the five. Five negatives inside one mechanism = change
layer. The alphabet has ~13 mechanisms — a full sweep is ~15-30 cheap
GETs/POSTs, well inside the challenge budget.
