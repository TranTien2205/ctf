# Troubleshoot deep — diagnosing the silent mass-assignment failure

## "Field doesn't land" — the decision tree

```
canary sent → read-back checked → field absent?
├─ control shows the field too?     → serializer-hidden; exercise directly
├─ write response echoed it?        → echo-artifact; strict-schema drop
├─ `400`/`422`?                     → schema falsifier → other carrier
├─ `200` silent?                    → binder drop → nested → other endpoint
└─ cache-busted re-GET same?        → real drop → other carrier/endpoint
```

## "Field lands but nothing changes" — the inert pivot

The stored field's gate reads elsewhere. Find the gate's real field:

1. **diff a real admin's record** — `GET /api/users/<admin>` if
   readable; every key you lack is a candidate;
2. **read the gate's source** — `is_staff`, `permissions.includes`,
   `admin_users` join, `request.user.is_superuser`;
3. **the re-issue edge** — the bound `role` lands in the next JWT:
   re-login, re-hit the gate;
4. **the sibling semantic** — `role` inert → `is_staff`, `permissions`,
   `groups`, `access_level`.

## "Endpoint 400s on the control too" — baseline broken

The control body is wrong before the probe:

- field names: `username` vs `user` vs `name` — the form's real names;
- required params: `password_confirmation`, `terms`, a CSRF token;
- content-type mismatch: `application/json` body sent as form;
- the endpoint is admin-only / gated — the baseline can't reach it.

## "Field lands → 500" — the coercion crash

The binder TRIED; the type rejected. `role:"admin"` on an enum, `groups:
"admin"` on a join-array, `balance:"lots"` on a numeric column. The
right-typed variant may land: `role:1` (enum int), `groups:[{"id":1}]`
(FK array), `balance:99999` (numeric).

## "Everything drops it" — the binder-family falsifier

All conventional binders allowlist — check the non-conventional:

- `/import`, `/seed`, `/bulk`, `/migrate` — bulk binders;
- `/admin/*` — needs a privilege edge but the binder is widest;
- GraphQL mutations — args schema is a separate binder;
- method-override — `?_method=PUT` reaching a different handler;
- nested associations — `user[profile_attributes][role]` reaching the
  child model's fields.

## "The decision doesn't change" — the wrong gate

`/admin` isn't the gate — find the RIGHT one:

- the flag route (`/flag`, `/api/flag`, `/premium`, `/vault`);
- the privileged action (`POST /admin/users`, `GET /api/users` listing);
- the economic action (`/checkout` total, `/purchase/flag-item`);
- the state gate (`/verified-only`, `/onboarding-complete`).

The bound field opens whichever gate READS it — the gate inventory is
the decision map.

## "Two requests can't be diffed" — the contamination

Two fields in one canary — split into two canaries. The attribution
rule is absolute: one extra field per request.
