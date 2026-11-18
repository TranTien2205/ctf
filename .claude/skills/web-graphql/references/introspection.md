# Introspection — extracting the full schema

Introspection is the single highest-value request in a GraphQL assessment:
one POST returns every type, every query, every mutation, every argument and
every return shape the server will ever honor. This file gives the query set,
the parsing workflow, and the edge cases (disabled introspection is covered in
`introspection-off.md`).

---

## 1. The canonical full introspection query

This is the spec-complete document — send it first:

```graphql
query IntrospectionQuery {
  __schema {
    queryType { name }
    mutationType { name }
    subscriptionType { name }
    types {
      ...FullType
    }
    directives {
      name
      description
      locations
      args { ...InputValue }
    }
  }
}

fragment FullType on __Type {
  kind
  name
  description
  fields(includeDeprecated: true) {
    name
    description
    args { ...InputValue }
    type { ...TypeRef }
    isDeprecated
    deprecationReason
  }
  inputFields { ...InputValue }
  interfaces { ...TypeRef }
  enumValues(includeDeprecated: true) {
    name
    description
    isDeprecated
    deprecationReason
  }
  possibleTypes { ...TypeRef }
}

fragment InputValue on __InputValue {
  name
  description
  type { ...TypeRef }
  defaultValue
}

fragment TypeRef on __Type {
  kind
  name
  ofType {
    kind
    name
    ofType {
      kind
      name
      ofType {
        kind
        name
        ofType {
          kind
          name
          ofType {
            kind
            name
            ofType {
              kind
              name
              ofType {
                kind
                name
              }
            }
          }
        }
      }
    }
  }
}
```

Send it URL-encoded as JSON:

```bash
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  --data-binary @introspection.json > schema.json
```

or via the repository tool which wraps it:

```bash
python3 tools/web/graphql_probe.py introspect --url "$BASE/graphql" \
  --headers "Authorization: Bearer $TOKEN" > /tmp/intro.json
```

`graphql_probe introspect` sends the bounded `__schema` query and prints a
summary (types, root fields, mutations) — read it before grepping the raw JSON.

## 2. Smaller queries when the full one is refused

Some servers cap query size or depth but still allow introspection — the
document above trips a depth/cost limit *without* meaning introspection is
off. Degrade gracefully in order:

```graphql
# Level 1 — types only
{__schema{types{name kind}}}

# Level 2 — types + field names
{__schema{types{name kind fields{name}}}}

# Level 3 — root types
{__schema{queryType{name fields{name args{name type{name kind ofType{name kind}}}}}}
        mutationType{name fields{name args{name}}}}

# Level 4 — one type at a time
{__type(name:"Query"){name fields{name args{name type{name kind ofType{name}}}}}}
{__type(name:"Mutation"){name fields{name}}}
{__type(name:"User"){name fields{name type{name kind ofType{name kind}}}}}
```

Strategy: fetch `Level 1` for the type list, then `Level 4` per interesting
type. That is ~N+1 requests but each is tiny — depth limiters pass it.

## 3. Reading the result — what to extract

From `data.__schema`, produce these working lists before touching resolvers:

```bash
# root operation surfaces
jq '.data.__schema.queryType.name, .data.__schema.mutationType.name,
    .data.__schema.subscriptionType.name' schema.json

# every query field with args
jq -r '.data.__schema.types[] | select(.name=="Query").fields[]
       | "\(.name)(\([.args[].name]|join(", ")))"' schema.json

# every mutation
jq -r '.data.__schema.types[] | select(.name=="Mutation").fields[]
       | "\(.name)(\([.args[].name]|join(", ")))"' schema.json

# interesting type names
jq -r '.data.__schema.types[].name' schema.json \
  | grep -iE "flag|admin|secret|token|user|key|internal|debug|config|cred|file|role|perm|private"

# every custom directive — directive surface is attack surface
jq -r '.data.__schema.directives[] | "\(.name) @\(.locations|join(","))"' schema.json
```

High-value targets, in order:

1. **Fields named for secrets**: `flag`, `secret`, `token`, `apiKey`,
   `password`, `credential`, `debug`, `internal`, `admin`, `config`, `env`,
   `session`, `jwt`, `private`, `hidden`, `backdoor`.
2. **Mutations that change privilege**: `updateUserRole`, `setAdmin`,
   `promoteUser`, `grantPermission`, `updatePermissions`, `makeAdmin`,
   `verifyUser`, `resetPassword`, `changeRole`.
3. **List/read fields on sensitive types**: `users`, `allUsers`, `user(id:)`,
   `sessions`, `orders`, `documents`, `files`, `logs`, `auditLog`.
4. **Node/entity interfaces**: `node(id:)`, `nodes(ids:)` — Relay's global
   object fetch, a built-in IDOR surface (`node-interface.md`).
5. **Schema meta**: `__schema`, `__type` still reachable (introspection is
   per-field controllable — some servers leave `__type` on while `__schema`
   is blocked).
6. **Federation entries**: `_service`, `_entities`, `_any`, `_representations`.

## 4. Hidden / undocumented fields

The front-end calls a *subset*. The schema is the whole truth. Compare:

```bash
# fields the app actually calls — grep the bundle for operation docs
grep -oE "query [A-Za-z_]+ ?\{[^}]*" /tmp/bundle -r | sort -u > /tmp/app-queries.txt

# fields the schema offers
jq -r '.data.__schema.types[] | select(.name=="Query").fields[].name' \
   schema.json | sort -u > /tmp/schema-queries.txt

comm -13 /tmp/app-queries.txt /tmp/schema-queries.txt
```

Every line in the second list but not the first is an unexercised resolver —
each one gets a direct probe (`idor-graphql.md`, `authz-bypass.md`).

## 5. Introspection responses worth double-checking

| Result shape | Meaning | Next step |
|---|---|---|
| Full `__schema` | open season | schema-analysis.md |
| `{"errors":[{"message":"GraphQL introspection is not allowed"}]}` | explicitly disabled | introspection-off.md |
| `{"data":{"__schema":null}}` | disabled by returning null | introspection-off.md |
| `{"errors":[{"message":"Cannot query field \"__schema\""}]}` | introspection fields stripped | `__type` probe; then introspection-off.md |
| 400 depth/cost error | document too big, not off | level-2 queries above |
| 401/403 | auth gate at HTTP layer | get any session; re-introspect per role |
| Schema filtered by role | some types only visible to admin | record; hunt resolvers directly (they still resolve even when invisible!) |

**Critical**: a type hidden from your role's introspection view is usually
still *resolvable* — schema filtering is cosmetic unless the resolver checks
authz itself. Try the field even when introspection doesn't show it
(`authz-bypass.md`).

## 6. __type side-channel when __schema is blocked

`__type(name: "Query")` is a separate introspection field; several disabling
middlewares only catch `__schema`:

```graphql
{__type(name:"Query"){name fields{name args{name type{name kind ofType{name kind}}}}}}
{__type(name:"Mutation"){name fields{name}}}
{__type(name:"User"){fields{name type{name}}}}
```

Walk the type graph by reading field types: `Query` returns types, each type's
fields return more types. Seven nested `ofType` unwraps cover NonNull/List
wrapping to any practical depth.

## 7. Persisted-query gate detection

If the endpoint answers *every* free-form query with
`PersistedQueryNotAllowed` / `PersistedQueryNotFound`, it uses Apollo's APQ or
an allowlist — free-form introspection is dead by design, not by bug. Jump to
`persisted-queries.md` for the bypass surface (hash registration, unregistered
hashes, APQ cache poisoning).

## 8. Automation shape

The introspection output feeds every downstream module. Cache it once:

```bash
python3 tools/web/graphql_probe.py introspect --url "$BASE/graphql" > schema.json
python3 tools/state.py $CHAL --hypothesis "schema exposes $(jq '.data.__schema.types|length' schema.json) types"
```

Record the disclosure itself through the hooks:

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {__schema{types{name}}}' \
  --verdict confirms --evidence-kind class --class web-graphql \
  --hypothesis-id h1 \
  --evidence '"types":[{"kind":"OBJECT","name":"Query"' \
  --response '<verbatim introspection response excerpt>'
```

Schema disclosure is a *capability*, not yet a finding. The finding is the
unauthorized read/mutation you reach from it — that is what `post-probe
--verdict confirms --evidence-kind impact` is for.
