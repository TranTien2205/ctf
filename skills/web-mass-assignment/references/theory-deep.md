# Theory deep — why mass assignment is a structural bug, not a mistake

## The convenience-security inversion

Frameworks add binding to save developer effort: `User.create(params)`
replaces `user.name = params[:name]; user.role = params[:role]; ...`
per field. The convenience is *coverage* — bind everything, let the
developer subtract the dangerous fields. The security model inverts:
safety is the exception, not the default. Every mass-assignment bug is
a subtraction the developer didn't make — and subtraction is the
action humans forget most reliably.

## The three defense models and their failure modes

| Model | Mechanism | Failure |
|---|---|---|
| bind-all-subtract | everything binds; allowlist subtracts | allowlist forgotten / wrong / per-endpoint drift |
| allowlist-add | nothing binds unless declared | declared set too wide / nested tunnel / shared list |
| schema-first | schema validates input | validates TYPES not admission; different schema per endpoint |

Every failure is the same shape: the bound coverage exceeds the
intended coverage. The bug isn't any one mechanism — it's the gap
between what the binder CAN write and what the form SHOULD send.

## The reach graph as the risk model

```
field → binder → model → gate → resource
role → PATCH   → User  → check_admin → /admin
```

The risk isn't the bound field — it's the DECISION the field reaches.
`role` bound but unread is null; `role` bound and read by `check_admin`
is critical. The reach graph maps: which fields are bindable (the
binder surface) → which decisions read them (the gate map) → which
resources the gates protect (the flag path). The exploit is the
shortest path in that graph.

## Why it survives audits

- **invisible surface**: the writable fields aren't visible in the UI —
  the reviewer sees the form, not the model;
- **per-endpoint drift**: `permit` on register is tight, `permit` on
  PATCH is wide — each looks correct in isolation;
- **shared helpers**: one `strong_params`/`fillable`/`Bind` serving
  both admin and public endpoints — the admin's wider list leaks to
  the public;
- **serializer divergence**: the field stores but never returns —
  read-back can't see it; the decision can;
- **type-coercion hiding**: `role:1` looks harmless; the enum makes
  `1` = admin.

## The second-order reach

The bound field unlocks a WIDER binder: `role:admin` → `POST /admin/
users` → the admin binder's own mass-assignment (`flag_visible:true`,
`internal_note`, `clearance`). The reach graph includes edges where
the bound field opens a second binder — the exploit chains binders.

## The falsifier-depth model

A falsifier isn't "class dead" — it's "this cell dead." The binder
matrix is `endpoint × carrier × content-type × method × field-semantic`;
a `400` on JSON kills the JSON row, not the matrix. The class is dead
only at the model depth (no privileged fields exist) or binder-family
depth (every binder allowlisted). Depth-annotated falsifiers are the
honest map — `endpoint falsifier` means the OTHER endpoints are still
live.

## Why the class is persistent

The bug re-appears whenever a new endpoint binds a model — every
`POST`/`PATCH`/`PUT`/`GraphQL`/bulk endpoint is a fresh binder with a
fresh allowlist decision. The class isn't a vulnerability; it's a
vulnerability PATTERN that every binder-writing decision re-opens.
