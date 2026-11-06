# GraphQL

**When:** a single endpoint taking a query document - `/graphql`, `/gql`,
`/api/graphql`, or any POST with `{"query": "..."}`.

## Recon: introspection

```graphql
{__schema{queryType{name}mutationType{name}types{name fields{name type{name}}}}}
```

On: full schema in one shot - dump it, map every query/mutation. Off:
field-name guessing from front-end JS (js_recon), error suggestions
("Did you mean..."), and `__typename` probes.

## Bug classes that pay

1. **Missing authorization per field/object** - introspect for `user`,
   `admin`, `orders`, `payments` fields; query them with your low-priv
   token. BOLA on node ids (base64 `User:123`) - same rule as `idor`:
   one foreign object proves it.
2. **Mutations without CSRF protection** - GraphQL-over-GET or
   form-encoded `application/x-www-form-urlencoded` body with `query=`
   means a plain form can fire mutations cross-origin (see `csrf`).
3. **Batching/alias abuse** - `[{q1},{q2},...]` or `a:login(...)` xN:
   rate-limit bypass on login mutations (brute force inside one request).
4. **Nested depth DoS** - deeply cyclic query; send ONE bounded example,
   never a real attack on a shared service.
5. **Injection inside resolvers** - arguments flow into SQL/shell/LDAP;
   probe argument values like normal params (sqli/cmdi).
6. **Debug artifacts** - Apollo/GraphiQL explorer, `debug` errors, stack
   traces with file paths, `extensions` leaking internals.

## Reading responses honestly

`"data": {"x": null}` + error array = resolver rejected - not access.
A field returning another user's non-null data = the evidence quote.

## Falsifier

Introspection off AND every sensitive field returns auth errors under a
low-priv identity AND mutations enforce content-type + token checks.

## Severity guide

Cross-object reads of PII: high. Admin mutation reachable: critical-high.
Rate-limit bypass on auth mutation: medium. Introspection on production
alone: info-low.
