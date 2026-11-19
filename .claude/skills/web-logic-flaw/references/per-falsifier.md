# Per-falsifier map — each falsifier, what it proves, and where to go next

A falsifier firing is never "nothing found" — it proves a specific
defense exists, and each defense has its own bypass surface. This map
pairs every falsifier with what it proves and the legitimate next move.

## `role: user` on read-back after `role=admin`

- **Proves**: allowlist binding on this endpoint's binder.
- **Next, legitimate**: `PATCH`/`PUT` on the same model (a different
  binder), nested-object and array paths (the allowlist may be
  shallow), method-override (`_method=PUT`).
- **Dead**: spelling variants of `role` on the SAME endpoint.

## `400 unknown field: role`

- **Proves**: strict schema — the schema layer rejects before binding.
- **Next**: content-type shift (the form binder may not share the JSON
  schema), the update endpoint, a sibling endpoint sharing the model.
- **Dead**: any field name on this content-type — the schema answers
  for all of them.

## `302`/`400` to earlier step on a workflow skip

- **Proves**: a real server-side state machine ordering the flow.
- **Next**: find WHERE the state lives — unsigned cookie/params forge
  it; server session is solid but the TERMINAL endpoint may still be
  unguarded (`/flag`, `/export` bare).
- **Dead**: skipping to mid-flow steps — the ordering holds.

## `409 already redeemed` on serial replay

- **Proves**: a consumed-marker exists.
- **Next**: key-scope probes — same `(user,code)` vs `requestId`-keyed
  vs cross-user; the parallel window is `web-race-condition`'s.
- **Dead**: serial identical replays — the marker answers.

## `400 quantity must be positive` (and friends)

- **Proves**: field-level validation on THIS field.
- **Next**: the OTHER numeric fields — `price`, `discount`, `tax`,
  `shipping` are different layers; also non-sign boundaries on the same
  field (`NaN`, `1e309` exercise different guard polarity).
- **Dead**: sign variants (`-2`, `-999`) — the sign check answers all.

## Silent clamp (`200`, value normalized)

- **Proves**: a clamp, not a check — the bound exists and normalizes.
- **Next**: is the clamp consistent? Some apps clamp `quantity` but
  not `discount`; also probe where the clamped value gets used vs the
  raw one (a clamp in display, raw in arithmetic).
- **Dead**: the same field's boundaries — the clamp answers.

## Identical rejection: out-of-limit vs malformed

- **Proves**: the transform is checked too, or absent — the Pachinko
  falsifier on this target.
- **Next**: different transform shapes — is there ANOTHER transform
  (decode, unit, coerce) on a different field with the same check-first
  structure?
- **Dead**: more `id` values past the limit — the check's range is
  mapped.

## `403` on foreign `objectId`

- **Proves**: ownership enforced — IDOR's falsifier too.
- **Next**: is the ownership check on the OBJECT or the OPERATION?
  `GET /order/999` 403s but `POST /order/999/confirm` may not — the
  transition path can skip the read path's check.
- **Dead**: direct object reads — ownership answers.

## `409` on second privileged object

- **Proves**: singleton uniqueness enforced.
- **Next**: is uniqueness on the right field? Unique on `username`
  doesn't stop a second `role=admin` object; unique on `email` doesn't
  stop `admin@x` vs `Admin@x` case variants.
- **Dead**: identical second-object requests.

## `400 price mismatch` on mutated upstream value

- **Proves**: the server recomputes — trust-in-earlier-step dead at
  this value.
- **Next**: which values does it NOT recompute? `total` recomputed says
  nothing about `discount`, `tax`, `shipping`, `currency` — each
  carried value is its own layer.
- **Dead**: re-spelling the recomputed field.

## `400 invalid expiry` on time values

- **Proves**: server-side time validation.
- **Next**: WHICH comparisons are checked — expiry yes, `notBefore`?
  `createdAt`? Each time field is a layer; also probe the comparison
  boundary (`expiry == now` — inclusive vs exclusive).
- **Dead**: the same field's time values.
