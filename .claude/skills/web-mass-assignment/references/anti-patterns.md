# Anti-patterns — mass-assignment moves that look right but aren't

## 1. The payload-list blast

Firing 100 field names at one endpoint — 95 aren't on the model. The
dictionary covers SEMANTICS, not spellings; the high-frequency set
(`role`, `is_admin`, `verified`, `balance`, `permissions`, `groups`)
reaches most models. `binding_probe.py`'s default set is the shortlist.

## 2. The echo-as-proof

`POST` echoes `{"role":"admin"}` → "stored!" The echo is the parser's
view; the store may drop it. Read-back through a DIFFERENT endpoint is
the only storage evidence.

## 3. The inert-field finding

`role:"admin"` stored, `/admin` `403`s — recorded as a solve. The class
bar: a stored field never read is a NULL result. The bound field must
CHANGE a decision; find the field the gate reads.

## 4. The single-carrier conclusion

`role` dropped on JSON → "class dead." Form/multipart/query/PATCH —
four more carriers, four more cells. A falsifier closes ONE cell.

## 5. The spelling sweep

`role`, `isAdmin`, `admin_flag`, `ROLE`, `access_level` — one semantic,
five probes. The model answers the SEMANTIC; the falsifier on `role`
covers `isAdmin`. Probe the semantic space, not the spelling space.

## 6. The control-skip

`role:"admin"` on read-back — was `admin` the default? The control pair
(`{u,p}` vs `{u,p,role}`) is the attribution. Without it the diff is
ambiguous.

## 7. The writeup-payload trap

Copying a writeup's `{"is_admin":true}` onto a challenge whose model
uses `role` — the writeup's field names are ITS schema's. The field
inventory is per-target.

## 8. The PUT-wipe

`PUT /users/me {"role":"admin"}` — replace zeroed the rest; the account
broke. PUT needs the FULL control body + extras.

## 9. The another-user probe

`PATCH /users/9` on another's record — the IDOR-adjacent mistake + a
rules violation. Probe your own `me`.

## 10. The register-only audit

`POST /register` tight → "no mass assignment." The `PATCH`/`PUT` binder
is usually the wide one — probe the update endpoint FIRST.

## 11. The cached falsifier

`GET` `role:"user"` from a cached view → falsifier recorded. Re-GET
fresh (`?cb=<rand>`) before concluding.

## 12. The two-field canary

`{"role":"admin","verified":true}` — which caused the diff? ONE extra
field per request; split into two canaries.
