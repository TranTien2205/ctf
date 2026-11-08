# Binding shapes

Mass assignment exists wherever request input is bound into an object with
more fields than the form exposes. The payload is always the same idea: send
the field the client never sends.

## Finding the field names

- Read the object back first (`GET /api/me`, order detail, profile) — every
  returned key is a candidate writable key.
- JS bundles and sourcemaps name them: search the bundle for `role`, `admin`,
  `is_staff`, `balance`, `price`, `discount`, `approved`, `verified`, `status`,
  `plan`, `credits`.
- Error messages leak field names: send a wrong-typed value and read the
  validation error listing the expected schema.
- Documentation endpoints (`/api/docs`, swagger) spell the model out.

## Carrier shapes

| Shape | Payload |
|---|---|
| Flat JSON | `{"name":"x","role":"admin"}` |
| Prefixed (Rails/Laravel-style) | `user[role]=admin` or `{"user":{"role":"admin"}}` |
| Form | append `&role=admin` to the declared fields |
| Deep merge | `{"billing":{"price":0}}` — patch endpoints merge nested objects |
| Repeated key | `role=user&role=admin` — binder takes first or last |
| Pollution-adjacent | `constructor.prototype` is NOT this class — see web-prototype-pollution |

## Confirmation

The write landing is not enough — the field must change a decision:

1. Submit with the extra field; read the object back — field stored?
2. Exercise the field's meaning: a `role` that unlocks an admin route, a
   `price` the checkout totals from, an `approved` flag that gates access.
3. Quote the proving response verbatim (the admin route's 200, the total).

## Traps

- A field stored but unread is a null result — record it, do not cite it.
- PATCH vs PUT: PUT replaces, PATCH merges — the merge is where extra fields
  survive unnoticed.
- Read-after-write can hit a cached view; fetch a second representation
  (detail page, `/api/me`) before calling it negative.
