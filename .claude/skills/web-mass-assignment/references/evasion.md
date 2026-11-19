# Evasion — getting the extra field past filters and validators

## The filter positions

The extra field can be filtered at three points, each bypassable
differently:

| Position | Filter | Bypass |
|---|---|---|
| client | JS strips the field from the body | send the raw request — JS isn't the wire |
| proxy/WAF | param allowlist at the edge | content-type shift; param casing; dupes |
| schema | `unknown property` at the parser | form/multipart carrier; nested under allowed parent |
| binder | silent drop at the model | the update endpoint; the allowed-parent tunnel |

## Client-side stripping

The JS builds `{username, password}` — the extra `role` isn't sent
because the CODE doesn't include it, not because the server rejects it.
Intercept the request and add the field — the JS constraint is a
client-side fiction.

## WAF/param-allowlist evasion

- **Content-Type shift**: `role` rejected on JSON → `role=admin` on
  `application/x-www-form-urlencoded` (different param parser, maybe
  different allowlist).
- **Case**: `Role`, `ROLE` — case-insensitive binders (ASP.NET)
  accept what case-sensitive filters miss.
- **Duplicate keys**: `{"role":"user","role":"admin"}` — the filter
  reads first, the binder takes last.
- **Nested tunnel**: `{"profile":{"role":..}}` — the filter checks
  top-level only; the deep merge reaches the nested field.
- **Array wrap**: `role=["admin"]` or `role[]=admin` — the filter
  checks scalars, the binder accepts arrays.

## Schema-bypass via content-type

The `400 unknown property` is the JSON parser's schema — the SAME model
bound through the form path has a different parser (maybe no schema).
`curl -d 'role=admin'` vs `curl -d '{"role":"admin"}'` — two parsers,
one model.

## Prefix/nesting conventions

- Rails/PHP: `user[role]=admin`, `user[role][]=admin`;
- qs/dotted: `user.role=admin`;
- nested JSON: `{"user":{"role":..}}`, `{"profile":{"role":..}}`;
- array-of-objects: `{"roles":[{"name":"admin"}]}`,
  `{"groups":[{"id":1}]}`.

The allowlist covers `user`/`profile` as a unit; the nested merge
reaches the field the flat allowlist would drop.

## Method-override routing

`POST` + `X-HTTP-Method-Override: PUT` or `?_method=PATCH` — the
validation layer sees POST, the handler runs PUT's binder. Different
allowlists on different methods make the override a carrier.

## Type-coercion tunnels

- `role:true` (bool) where `role:"admin"` (string) was filtered —
  typed columns coerce;
- `role:1` → the enum's integer representation;
- `balance:0.001` float-precision vs `balance:1e6` exponential;
- `verified:"yes"`/`"1"`/`true` — coercion variants on boolean fields.

## The PATCH-merge tunnel

`PATCH` deep-merges: `{"settings":{"admin":true}}` writes
`settings.admin` inside the existing object — the field the flat
schema rejects survives nested inside an allowed object key.
