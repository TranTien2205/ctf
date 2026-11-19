# Glossary deep — mass-assignment terms with mechanics

- **binder** — the framework layer mapping request params into model
  attributes. Implementations: `Object.assign`, `permit`, `fill`,
  `[Bind]`, `**kwargs`, `setattr` loop, `ShouldBindJSON`. The bug lives
  in its coverage — what it copies vs what the form sends.

- **allowlist** — the field set the binder accepts. Forms: `permit(...)`,
  `$fillable`, `pick`, `[Bind(Include)]`, `fields=`, `Meta.fields`.
  Its ABSENCE or WIDTH is the bug — a list that includes `role` is as
  exploitable as no list.

- **denylist** — the inverse: `attr_protected`, `$guarded`,
  `[Bind(Exclude)]`. Blocks named fields while allowing all others —
  forgetting a dangerous field is the denylist's gap.

- **mass assignment** — binding request-supplied fields beyond the
  declared form. The class name; the bug shape.

- **over-posting** — the .NET/ASP.NET name for the same class: posting
  more fields than the form declares.

- **canary field** — the extra field added to a probe request. Its
  landing on the read-back is the signal; its absence is the falsifier.

- **control** — the request WITHOUT the canary. The baseline for
  attribution; the control/canary pair is the experimental design.

- **read-back** — a `GET` on the affected object through a DIFFERENT
  endpoint than the write. The store's truth vs the write's echo.

- **echo** — the write response's own view. May show bound-then-
  dropped fields (Mongoose `strict`) or bound-then-hidden fields
  (serializer). Never storage evidence.

- **inert field** — a bound field that stores but changes no decision.
  The class bar: a NULL result, not a finding.

- **serializer-hidden** — a stored field never returned by any
  representation (`toJSON`/`fields=`/`as_json`). Provable only by
  exercising the decision.

- **nested tunnel** — `{"profile":{"role":..}}` reaching a nested field
  the flat allowlist can't drop (the parent is allowed as a unit).

- **deep merge** — recursive object merge (`_.merge`, `deepmerge`,
  `Object.assign` nested) — the nested-tunnel mechanism; also the
  `__proto__`-walk vector (pollution overlap).

- **kwargs merge** — `User(**json)` — the kwargs signature IS the
  allowlist; `TypeError` names rejected keys (schema leak).

- **prefixed params** — `user[role]`, `user.role`, `User.Role` —
  Rails/PHP/.NET nesting conventions reaching model fields.

- **discriminator** — `_t`/`__t`/`type`/`user_type` — the field
  selecting WHICH schema binds. Binding it switches to the privileged
  variant.

- **strong params** — Rails' `permit`/`require` — the per-action
  allowlist. Sharing one `permit` across admin+public endpoints is
  the shared-allowlist bug.

- **fillable/guarded** — Laravel's `$fillable` (allowlist) /
  `$guarded` (denylist) — model-level admission control.

- **PUT wipe** — replace semantics zeroing omitted fields — probe PUT
  with the FULL control body + extras.

- **decision exercise** — hitting the gated route/total/state the
  bound field should change. The second confirm leg; the exploit.

- **falsifier depth** — which layer killed the probe: content-type →
  endpoint → binder-family → model → semantic. Each closes different
  cells.

- **cell** — one `(endpoint, carrier, content-type, method, field)`
  combination in the falsifier matrix. The map's unit.

- **reach graph** — `field → binder → model → gate → resource`. The
  exploit is the shortest path in that graph.
