# Per-mechanism map — each business-logic mechanism, its probe and falsifier

## mass-assignment

- **Signal**: model has fields the form doesn't send (`role`, `balance`,
  `verified`, `permissions`, `plan`, `flags`, `owner`, `__proto__`).
- **Probe**: `register`/`update` with the extra field → read-back via GET.
- **Confirm**: `role: admin` (or the sent privileged value) in read-back.
- **Falsifier**: `role: user` on read-back, or `400 unknown field`.
- **Layer note**: nested (`user.role`), array (`role[]`), and dotted
  conventions reach different binder code paths — one negative doesn't
  close all three, but an allowlist closes the whole mechanism.

## workflow-skip

- **Signal**: multi-step flow — cart→pay→confirm, register→verify→activate.
- **Probe**: call a later step directly; GET terminal endpoints bare.
- **Confirm**: `200` + forbidden state (`status: confirmed`, `charged: 0`).
- **Falsifier**: `400/302` to the required earlier step.
- **Layer note**: state may live in the cookie (forge `step`), in the
  session (harder), or nowhere at all (terminal endpoint unguarded).

## state-replay

- **Signal**: one-time action — redeem, refund, vote, claim, reset token.
- **Probe**: run the transition twice serially.
- **Confirm**: effect applies twice (`balance +50` then `+50` again).
- **Falsifier**: `409`/`400 already used` on the second.
- **Layer note**: serial replay is the logic-flaw shape; parallel replay
  is `web-race-condition`'s. Serial first — always.

## numeric-boundary

- **Signal**: arithmetic on user values — totals, prices, discounts.
- **Probe**: the boundary alphabet — `-1`, `0`, `-0`, `NaN`, `Infinity`,
  `1e309`, int32/uint32 wraps, hex/octal, strings, arrays.
- **Confirm**: forbidden state — negative total, free order, `NaN`
  accepted into a confirmed state.
- **Falsifier**: `400`/clamp per value.
- **Layer note**: a validated `quantity` says nothing about `price` or
  `discount` — different fields are different layers; different VALUES on
  one field are different parser paths, not spelling variants.

## scaling-after-check (Pachinko)

- **Signal**: an index/ID that the app transforms — offset, scale,
  encode, decode — before use.
- **Probe**: `id` at the documented limit, then limit+1, then word-size
  boundaries; compare rejection SHAPES vs a malformed-ID rejection.
- **Confirm**: a different-layer rejection or acceptance where docs
  forbid — the transform ran and the check didn't cover its output.
- **Falsifier**: identical rejection for out-of-limit and malformed IDs —
  transform checked or absent.
- **Layer note**: three bounds — UI's, checker's, effective-after-
  transform. Compute the wrap target: `id` such that `off + id*S ≡ target
  (mod 2^w)`.

## unit-confusion

- **Signal**: values with implicit units — price in cents vs dollars,
  weights, rates, currencies.
- **Probe**: send the value in the "other" unit — `price=100` where the
  client would send `1.00`.
- **Confirm**: charged/recorded at the wrong scale (`100` vs `1.00`).
- **Falsifier**: canonical normalization — `100` consistently means one
  thing.

## role-assignment

- **Signal**: privilege fields at object-creation time.
- **Probe**: as mass-assignment, focused on role/permission fields.
- **Falsifier**: allowlist (identical to mass-assignment — they're the
  same mechanism with different stakes).

## idempotency

- **Signal**: actions that should happen exactly once.
- **Probe**: replay with same `Idempotency-Key`/body; replay with mutated
  body + same key; replay cross-user.
- **Falsifier**: `409` on exact replay.

## time-assumption

- **Signal**: `expiry`, `notBefore`, `createdAt`, `timestamp` in client
  reach.
- **Probe**: past expiry, future notBefore, boundary `now`, epoch edges.
- **Falsifier**: server-side time check rejects (`400`).

## sequence-assumption

- **Signal**: monotonic IDs assumed to only move forward.
- **Probe**: replay an old ID; submit `sequence`/`nonce` out of order.
- **Falsifier**: `409`/`400` on stale sequence.

## ownership-assumption

- **Signal**: operations reference objects by ID.
- **Probe**: substitute another user's object ID inside the operation.
- **Falsifier**: `403` — and then it's IDOR, route there.

## singleton-assumption

- **Signal**: a "the" object — the admin, the config, the flag holder.
- **Probe**: create a second one.
- **Falsifier**: `409`/uniqueness.

## trust-in-earlier-step

- **Signal**: values that echo upstream → downstream (price carried in a
  hidden field, a `token` minted at step 1 trusted at step 3, headers
  trusted at the boundary).
- **Probe**: modify the upstream value between mint and use.
- **Falsifier**: server recomputes — `400 price mismatch`.
