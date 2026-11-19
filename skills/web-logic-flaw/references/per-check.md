# Per-check map — the check the handler makes vs the edge it leaves open

Every state-changing handler checks *something*. The logic flaw lives in
the difference between what it checks and what the workflow needs. This
module maps common check shapes to the edge they leave.

## "The object exists" checks

| The check | The gap it leaves | The probe |
|---|---|---|
| `order exists` | order's *state* unchecked | `/confirm` on an unpaid order |
| `user exists` | user's *role* unchecked | admin op on a self-registered user |
| `code exists` | code's *consumed* bit unchecked | replay the redeem |
| `session exists` | session's *step* unchecked | call step 3 with a step-1 session |
| `token exists` | token's *expiry/use-count* unchecked | replay or age the token |

## "The field is well-formed" checks

| The check | The gap it leaves | The probe |
|---|---|---|
| `quantity is int` | sign unchecked | `-1` |
| `quantity > INT_MIN` | upper bound / wrap unchecked | `2147483648` |
| `price is numeric` | NaN/Infinity are numeric | `NaN`, `1e309` |
| `id is int` | transform output unchecked | `id` where `off+id*S` wraps |
| `amount is float` | unit unchecked | `100` where `1.00` expected |
| `date parses` | direction unchecked | expiry in the past |

## "The field is allowlisted" checks

| The check | The gap it leaves | The probe |
|---|---|---|
| body fields in allowlist | nested-object fields | `{"user":{"role":"admin"}}` |
| shallow merge | deep merge reachable | `__proto__`, `constructor` |
| allowlist on create | different allowlist on update | `PATCH` with `role` |
| allowlist on `POST` | none on `PUT`/`PATCH` | method change |
| schema validates types | schema allows extra fields | `additionalProperties` true |

## "The precondition ran" checks

| The check | The gap it leaves | The probe |
|---|---|---|
| `step1_done` flag in session | flag is client-readable cookie | forge the cookie bit |
| `paid` computed at step 2 | never re-checked at step 3 | skip to step 3 |
| token minted at step 1 | not bound to *this* flow instance | reuse token across flows |
| `Referer`/`Origin` present | header value unchecked | set the header directly |

## "Uniqueness" checks

| The check | The gap it leaves | The probe |
|---|---|---|
| unique on `username` | not on `email`, `role`, `flag-holder` | second privileged object |
| unique per-user | not per-object or global | cross-user replay |
| dedup on key | key is client-chosen | same key + mutated body |

## Reading the check from the response

The rejection text names the layer:

| Rejection | The layer that fired |
|---|---|
| `invalid input` / `400` generic | transport/schema validator |
| `role is not allowed` | binder allowlist |
| `payment required` / `302` to step | state machine |
| `already redeemed` | idempotency store |
| `id out of range` | the documented checker |
| *500/crash* on out-of-limit id | the transform — it ran unchecked |
