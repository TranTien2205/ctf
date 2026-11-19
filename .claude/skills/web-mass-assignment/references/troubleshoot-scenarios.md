# Troubleshoot scenarios — the failure modes and their fixes

## Scenario 1 — "the field just won't land, ever"

**Symptom**: `role`/`is_admin`/`verified` all drop on every endpoint.

**Causes, ordered**:
1. allowlist everywhere → try `{"profile":{"role":..}}` nested,
   `user[role]` prefixed, `/import`, GraphQL;
2. strict schema on JSON → try `role=admin` form, multipart;
3. model genuinely narrow → `GET` shows no privileged fields → the
   class is dead here; check OTHER models (`/wallets`, `/memberships`,
   `/orders`).

## Scenario 2 — "lands but the gate ignores it"

**Symptom**: `role:"admin"` stored, `/admin` `403`s.

**Causes**:
1. gate reads `is_staff`/`permissions` — try those;
2. gate reads a JWT claim — re-login, re-hit;
3. gate reads a join table — `{"membership":{"role":..}}` nested;
4. field IS the gate's but the value is wrong — `role:"superuser"`
   vs `"admin"`.

## Scenario 3 — "`400` on the control too"

**Symptom**: the documented body itself fails.

**Causes**:
1. wrong field names — `username` vs `user` vs `name`;
2. missing required params — `password_confirmation`, `terms`;
3. CSRF token missing on the form carrier;
4. content-type mismatch — JSON body sent as `text/plain`.

## Scenario 4 — "lands → `500`"

**Symptom**: the binder tries, the type crashes.

**Causes**:
- `groups:"admin"` on an array column → `groups:["admin"]` or
  `groups:[{"id":1}]`;
- `role:"admin"` on an enum `["user","mod"]` → `role:"mod"` or `role:1`;
- `balance:"lots"` on numeric → `balance:99999`.

## Scenario 5 — "the response echoes but the store doesn't"

**Symptom**: `{"role":"admin"}` in the POST response, `{"role":"user"}`
on the `GET`.

**Cause**: echo-artifact — Mongoose `strict` echoes bound-then-dropped
fields. The echo lies; the read-back is truth. Endpoint falsifier.

## Scenario 6 — "the GET is stale"

**Symptom**: `role:"user"` on read-back but the field should have
stored.

**Cause**: cached representation. Re-GET with `?cb=<rand>`; read
`/api/me` vs `/api/users/:id` vs the detail page; the field may show
on a different representation.

## Scenario 7 — "two requests differ in two ways"

**Symptom**: can't tell which field caused the diff.

**Cause**: two extra fields in one canary — `{"role":"admin",
"verified":true}`. Split into two canaries; the attribution rule is
ONE extra field per request.

## Scenario 8 — "PUT broke the object"

**Symptom**: `PUT {"role":"admin"}` → the account stopped working.

**Cause**: replace semantics zeroed `username`/`email`. PUT needs the
FULL control body + extras — `{"username":"x","email":"e","role":
"admin"}`.
