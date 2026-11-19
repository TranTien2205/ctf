# Glossary — mass-assignment terms

- **binder** — the framework layer mapping request params into model
  attributes (`Object.assign`, `permit`, `fill`, `[Bind]`, `**kwargs`).
- **allowlist** — the field set the binder accepts (`permit(...)`,
  `$fillable`, `pick`, `[Bind(Include)]`, `fields=`). Its absence or
  width is the bug.
- **mass assignment** — binding request-supplied fields beyond the
  declared form — the class name.
- **over-posting** — the .NET name for the same class.
- **canary field** — the extra field added to a probe; its landing on
  the read-back is the signal.
- **control** — the request WITHOUT the canary; the baseline for
  attribution.
- **read-back** — a GET on the affected object through a DIFFERENT
  endpoint than the write; the store's truth vs the write's echo.
- **echo** — the write response's own view; may show bound-then-dropped
  fields (Mongoose strict).
- **inert field** — a bound field that stores but changes no decision;
  a null result, not a finding.
- **serializer-hidden** — a stored field never returned by any
  representation; provable only by exercising the decision.
- **nested tunnel** — `{"profile":{"role":..}}` surviving a flat
  allowlist via deep merge.
- **discriminator** — `_t`/`type`/`__t` field selecting the schema;
  binding it switches to the privileged variant.
- **prefixed params** — `user[role]`, `user.role` — Rails/PHP/.NET
  nesting conventions reaching model fields.
- **deep merge** — recursive object merge (`_.merge`, `deepmerge`) —
  the nested-tunnel mechanism.
- **kwargs merge** — `User(**json)` — the signature IS the allowlist;
  `TypeError` names rejected keys.
- **schema falsifier** — `400/422 unknown property` — kills the
  content-type cell.
- **binder falsifier** — `200` + dropped on read-back — kills the
  endpoint's flat-key cell.
- **model falsifier** — no privileged fields exist — kills the class.
- **PUT wipe** — replace semantics zeroing omitted fields; probe PUT
  with the full body.
- **decision exercise** — hitting the gated route/total/state the
  bound field should change; the second confirm leg.
