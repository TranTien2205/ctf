# Evasion deep — the defense-layer internals and the paths around them

`evasion.md` is the field guide. This module reads the defenses —
what each layer inspects and exactly where its coverage ends.

## The schema layer

JSON-schema/`strict()` validators reject unknown keys on the JSON path.
Coverage ends at:

- **other content-types**: `application/x-www-form-urlencoded` and
  `multipart/form-data` are usually parsed by a different library with
  no schema — the field the JSON schema rejects binds through the form
  binder.
- **nested paths**: `additionalProperties:false` at depth-1 may not
  recurse — `{"profile":{"role":"admin"}}` passes if `profile`'s own
  schema is permissive.
- **sibling endpoints**: the schema is per-route — `/api/register`
  strict while `/register` legacy-form accepts.

## The binder allowlist

`pick(body, [...])`, `permit(...)`, `$fillable`, `[Bind(Include)]` —
coverage ends at:

- **the second binder**: `PATCH`/`PUT` handlers with their own pick-set
  — the profile update is meant to be editable, and its allowlist
  covers display fields while the model still carries `role`.
- **merge-then-pick ordering**: `pick({...defaults, ...req.body})` —
  the merge happens before the pick in some idioms.
- **prototype paths**: `__proto__` keys some merge libs walk —
  allowlist on own-properties doesn't cover prototype chain writes.

## The state-machine guard

Middleware checking `session.step` — coverage ends at:

- **the terminal**: `/flag`, `/export` often sit OUTSIDE the flow
  middleware — the guard protects the steps, not the prize.
- **parallel sessions**: state is per-session — a fresh session calling
  step 3 on a shared `orderId` tests per-object vs per-session state.
- **the carrier the guard reads**: `req.session.step` enforced while
  `req.body.step` is what the transition handler consumes — two
  different state bits, one checked one used.

## The dedup layer

The `409` on replay — coverage ends at:

- **key scope**: `(key,user)` dedup leaves cross-user replay;
  `(key,endpoint)` leaves cross-endpoint replay.
- **the check-set window**: `find` then `set` non-atomically — the
  parallel window (race's ground).
- **compensating actions**: redeem→refund→redeem — does the refund
  clear the consumed bit?

## The WAF / edge filter

Pattern-matching the raw request — coverage ends at:

- **encoding**: `%61dmin`, unicode-fullwidth `ａｄｍｉｎ`, overlong
  UTF-8 — the WAF sees bytes, the binder sees decoded keys.
- **structure**: `{"a":"ad","b":"min"}` split across concatenated keys;
  array-form `["ad","min"]` rejoined downstream.
- **the path the WAF doesn't cover**: alternate routes, method shifts,
  content-type shifts — the WAF guards a representation, not the model.

## The rate limiter

Not a mechanism defense — a budget one. `429` is not a falsifier.
Coverage is per-bucket: per-IP (`X-Forwarded-For` rotation where the
limiter trusts it), per-user (fresh account = fresh bucket), per-key.
The discipline: space writes, run reads during cooldown, never spray —
the challenge budget is the real constraint.

## The general evasion rule

Every defense covers a REPRESENTATION — a content-type, a key spelling,
a carrier, a session. The bypass question is always: which
representation of the same value does the SINK accept that the guard
didn't inspect? That's the same validator-gap sentence as Pachinko —
the checker bounds one representation, the sink consumes another.
