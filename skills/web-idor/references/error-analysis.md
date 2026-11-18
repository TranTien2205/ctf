# Error analysis — what the errors tell you

The error responses are a map of where the check sits and what it expects.

---

## 1. The status matrix

| Status | Meaning | Implication |
|---|---|---|
| `200` + data | reached | the object is readable — is it A's? |
| `200` + `{}`/`{"id":1}` | reached but sparse | exists, or a different object — not attributable |
| `302 → /login` | unauthenticated | session missing/expired |
| `302 → /` | forbidden-redirect | the check redirects instead of 403 |
| `400` | bad request | the id format failed validation |
| `401` | unauthenticated | token/credential issue |
| `403` | forbidden | the check ran and denied |
| `404` | not found | doesn't exist, OR the check hides existence |
| `405` | method not allowed | the method isn't routed |
| `500` | server error | the handler crashed — may leak |
| `503` | unavailable | down, not a check |

## 2. The `403` vs `404` differential

```
GET /users/1   → 403   # exists but denied
GET /users/9999 → 404  # doesn't exist
```

`403` = "exists, you can't have it"; `404` = "no object". The
differential is the existence oracle — which ids are live.

## 3. The `404` = "hidden" bug

`404` on `GET /users/1` but the object exists (it's admin's) — the check
returns `404` to hide existence. The `404` isn't "guarded" — it's
"denied-but-disguised". The `.json`/`?format=`/method variant may return
the real `403`/`200`.

## 4. The `302` = "redirect" confusion

`302 → /` on `GET /admin/flag` — a check that redirects to home. This
is `403`-equivalent, not "unguarded". The `.json`/`?format=json` variant
may return `403`/`200` instead.

## 5. The `400` = "format" gate

`400 {"error":"invalid id"}` — the format check rejected `id=abc` before
the ownership check. The *format* valid id (`id=1`) reaches the ownership
check; the error says the format is the first gate.

## 6. The `500` = "the fetch returned null"

`500 {"error":"Cannot read 'owner_id' of null"}` — `obj = get(id)`
returned null but the check dereferenced `obj.owner_id`. The `500` says
the id resolved to nothing — the existence oracle.

## 7. The `500` = "the check crashed"

`500 {"error":"'NoneType' has no 'is_admin'"}` — the check ran on a
`session.user` that was `None`. The error exposes the check's expectation.

## 8. The error leaks the schema/field

```
{"error":"Field 'secret' not in User"}              — the field name
{"error":"Cannot cast 'abc' to int for 'user_id'"}  — the type
{"error":"Unknown property 'rolex'; did you mean 'role'?"}  — suggestion
{"error":"Mass assignment to 'role' not permitted"} — the guard
{"error":"'role' is not fillable"}                  — Laravel fillable
{"error":"Strong parameter violation: role"}        — Rails strong-params
{"error":"'role' is a protected attribute"}
{"error":"'is_admin' is a restricted field"}
{"error":"'password_hash' is not fillable"}
{"error":"'secret_key' is not a permitted attribute"}
{"error":"'api_key' is not a permitted attribute"}
{"error":"Additional property 'role' not allowed"}  — JSON schema
{"error":"unpermitted parameter 'role'"}            — Rails
{"error":"forbidden attribute 'role'"}
{"error":"readonly attribute 'role'"}
{"error":"'role' requires admin"}
{"error":"'role' requires elevated privilege"}
{"error":"'role' is admin-only"}
{"error":"'role' must be one of ['user']"}
{"error":"'role' cannot be changed"}
{"error":"'role' is immutable"}
{"error":"'role' is read-only"}
{"error":"'role' is a server-managed field"}
{"error":"'role' is a computed field"}
{"error":"'role' is a derived field"}
{"error":"'role' is a system field"}
{"error":"'role' is an internal field"}
{"error":"'role' is a reserved field"}
{"error":"'role' is a sensitive field"}
{"error":"'role' is a privileged field"}
{"error":"'role' is an internal attribute"}
{"error":"'role' is not writable"}
{"error":"'role' is not updateable"}
{"error":"'role' is not settable"}
{"error":"'role' is not modifiable"}
{"error":"'role' is not assignable"}
{"error":"'role' cannot be mass-assigned"}
{"error":"'role' cannot be modified"}
{"error":"'role' cannot be updated"}
{"error":"'role' cannot be set"}
{"error":"'role' cannot be written"}
{"error":"'role' cannot be edited"}
{"error":"'role' cannot be assigned"}
```

The `role`/`admin`/`readonly`/`protected`/`fillable`/`strong parameter`/
`not permitted`/`must be one of` error family — the error names the
guarded field and sometimes its valid values.

## 9. The error leaks the check's position

```
{"error":"Cannot read 'user_id' of null"}            — fetch returned null
{"error":"'session' has no 'user_id'"}               — session lookup
{"error":"'NoneType' has no 'is_admin'"}             — the check ran
{"error":"comparison of int and str"}                — type mismatch
{"error":"invalid literal for int()"}                — Python int cast
{"error":"Cast to ObjectId failed"}                  — Mongo ObjectId cast
{"error":"CastError: Cast to ObjectId failed"}       — mongoose
{"error":"BSONError: invalid ObjectId"}              — BSON
{"error":"BSONError: Argument passed in must be a string of 12 bytes or a string of 24 hex characters"}
{"error":"badly formed hexadecimal UUID string"}     — Python uuid
{"error":"'abc' is not a valid uuid"}
{"error":"24-character hex string required"}
{"error":"'abc' is not a valid ULID"}
{"error":"'abc' is not a valid Crockford base32"}
{"error":"invalid ObjectId 'abc'"}
{"error":"'abc' is not a valid Snowflake"}
{"error":"invalid nanoid 'abc'"}
{"error":"'abc' is not a valid base64"}
{"error":"invalid UUID 'abc'"}
{"error":"malformed id 'abc'"}
{"error":"'abc' cannot be cast to ObjectId"}
{"error":"'abc' is not a valid ObjectId, it must be a 12-byte input or a 24-character hex string"}
{"error":"input must be a 24 character hex string, 12 byte Uint8Array, or an integer"}
{"error":"12 bytes or 24-character hex string required"}
{"error":"invalid id 'abc'"}
{"error":"'abc' is not a valid id"}
{"error":"'abc' is not a valid identifier"}
{"error":"'abc' is not numeric"}
{"error":"'abc' is not an integer"}
{"error":"'abc' is not a number"}
{"error":"'abc' cannot be converted to int"}
{"error":"'abc' cannot be converted to float"}
{"error":"'abc' is not a valid format"}
{"error":"invalid format 'abc'"}
{"error":"'abc' does not match uuid format"}
{"error":"'abc' is not a valid UUID format"}
{"error":"'abc' is not a valid UUID string"}
{"error":"'abc' is not a valid UUID value"}
{"error":"'abc' cannot be parsed as UUID"}
{"error":"'abc' is not a valid uuid4"}
{"error":"'abc' is not a valid version-4 UUID"}
{"error":"'abc' is not a valid uuid-4"}
{"error":"'abc' does not conform to uuid format"}
{"error":"'abc' is not a recognized uuid format"}
{"error":"UUID('abc') is not a valid UUID"}
{"error":"badly formed hexadecimal UUID string"}
{"error":"'abc' must be a 36-character UUID"}
{"error":"'abc' is not a 36-character UUID"}
{"error":"'abc' is not a valid ULID"}
{"error":"invalid ULID 'abc'"}
{"error":"'abc' is not a valid Snowflake"}
{"error":"invalid Snowflake 'abc'"}
{"error":"'abc' is not a valid nanoid"}
{"error":"invalid nanoid 'abc'"}
{"error":"'abc' is not a valid cuid"}
{"error":"invalid cuid 'abc'"}
{"error":"'abc' is not a valid ksuid"}
{"error":"invalid ksuid 'abc'"}
{"error":"'abc' is not a valid xid"}
{"error":"invalid xid 'abc'"}
{"error":"'abc' is not valid base64"}
{"error":"'abc' cannot be decoded from base64"}
{"error":"'abc' is not a valid hex"}
{"error":"'abc' is not valid hex"}
{"error":"'abc' cannot be decoded from hex"}
```

The cast/format errors name the *expected* type — `ObjectId`, `UUID`,
`int`, `ULID`, `Snowflake`, `base64`, `hex` — which narrows the format.

## 10. The `403` family — the denial names the check

```
{"error":"Forbidden"}
{"error":"Access denied"}
{"error":"Unauthorized"}
{"error":"Not authorized"}
{"error":"Insufficient permissions"}
{"error":"Missing permission"}
{"error":"Permission denied"}
{"error":"Not the owner"}
{"error":"Not the owner of this resource"}
{"error":"This resource belongs to another user"}
{"error":"You do not own this resource"}
{"error":"You are not the owner"}
{"error":"You are not the owner of this object"}
{"error":"You are not authorized to access this resource"}
{"error":"You are not authorized to view this resource"}
{"error":"You are not allowed to access this resource"}
{"error":"You do not have permission to access this resource"}
{"error":"You lack the 'admin' role"}
{"error":"Requires 'admin' role"}
{"error":"Requires 'owner' role"}
{"error":"Requires 'staff' role"}
{"error":"Requires 'superuser' role"}
{"error":"'admin' role required"}
{"error":"Admin access required"}
{"error":"Admin privilege required"}
{"error":"Owner access required"}
{"error":"Elevated privilege required"}
{"error":"Privileged access required"}
{"error":"'admin' scope required"}
{"error":"'admin' claim required"}
{"error":"'admin' authority required"}
{"error":"'admin' entitlement required"}
{"error":"You lack the 'admin' scope"}
{"error":"You lack the 'admin' claim"}
{"error":"You lack the 'admin' authority"}
{"error":"You lack the 'admin' entitlement"}
{"error":"You lack the required permission"}
{"error":"You lack the 'admin' permission"}
{"error":"You lack the 'owner' permission"}
{"error":"You lack the 'read' permission"}
{"error":"You lack the 'write' permission"}
{"error":"You lack the 'admin:read' scope"}
{"error":"You lack the 'admin:write' scope"}
{"error":"You lack the 'read' scope"}
{"error":"You lack the 'write' scope"}
```

The `requires 'admin' role`/`You lack the 'admin' scope` error names
the exact privilege the check expects.

## 11. The `404` family — ambiguous

```
404                       — not found, or denied-but-disguised
{"error":"Not found"}
{"error":"Object not found"}
{"error":"Object 42 not found"}       — names the id → existence oracle
{"error":"User not found"}
{"error":"Resource not found"}
{"error":"No such object"}
{"error":"Not found or forbidden"}    — deliberately ambiguous
{"error":"404"}
```

A bare `404` vs a `404` that names the id — the latter leaks existence.

## 12. The "the error IS the flag" edge

`{"error":"flag{...}"}` — a verbose error handler returns the flag in
the message; the error is the surface.
