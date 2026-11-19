# Troubleshoot playbook — the diagnostic decision tree

## The top-level tree

```
canary sent → read-back checked → decision exercised → verdict
      │              │                   │
      ▼              ▼                   ▼
   400?          absent?              403?
   schema        hidden              gate reads
   falsifier     /dropped            elsewhere
```

## Branch 1 — `400`/`422` on the canary

**The schema rejected extras.**

- `400 "unknown property: role"` → content-type falsifier → try
  `role=admin` form, multipart, `{"profile":{"role":..}}` nested;
- `422` pydantic/zod → same — the validator layer;
- `TypeError: unexpected keyword` → kwargs signature → the signature's
  params are the writable set (the error leaks them).

## Branch 2 — `200`, field absent on read-back

**The binder dropped it.**

- `role:"user"` on read-back (control also `user`) → endpoint falsifier
  → try `{"profile":{"role":..}}` nested, `user[role]` prefixed,
  `PATCH`/`PUT`, `/import`;
- `role` absent entirely → serializer-hidden → exercise the decision
  directly (`GET /admin`);
- cached `user` → re-GET with `?cb=<rand>` or a second representation.

## Branch 3 — `200`, field present, decision unchanged

**The field stored but is inert.**

- `role:"admin"` stored, `/admin` `403` → the gate reads `is_staff`/
  `permissions`/a JWT claim → try `is_staff:true`, `permissions:["*"]`,
  re-login (the re-issued token carries `role`);
- find the gate's real field — `GET /api/users/<admin>` diff, the
  gate's source;
- record the inert field — a null result, not a finding.

## Branch 4 — `500` on the canary

**The binder tried, the type crashed.**

- `groups:"admin"` → `groups:["admin"]` or `groups:[{"id":1}]`;
- `role:"admin"` on an enum `["user","mod"]` → `role:"mod"` or `role:1`;
- `balance:"lots"` → `balance:99999`;
- the `500` says the binder TRIED — the right-typed variant may land.

## Branch 5 — the control `400`s too

**The baseline is broken.**

- wrong field names — `username` vs `user` vs `name` — check the form;
- missing required params — `password_confirmation`, `terms`, CSRF;
- the endpoint is gated (`403`/`401`) — the baseline can't reach it;
- content-type mismatch — JSON sent as `text/plain`.

## Branch 6 — the decision changes WITHOUT the bound field

**Attribution confusion — something else opened the gate.**

- the gate opened on the control too → `admin` may be the DEFAULT;
- the `200` came from a different change (a session flag, a cache);
- the bound field is inert; the decision was already open — verify
  the control `403`s before crediting the canary.

## Branch 7 — PUT/POST wipe or breakage

**The replace corrupted the object.**

- `PUT {"role":"admin"}` → account broke → PUT needs the FULL body;
- `POST /register` with extras → `400` on missing required params →
  the canary must carry all documented fields + the extra.

## Branch 8 — two requests, ambiguous diff

**Two fields in one canary.**

- `{"role":"admin","verified":true}` → which caused the diff? →
  split into two canaries; ONE extra field per request.
