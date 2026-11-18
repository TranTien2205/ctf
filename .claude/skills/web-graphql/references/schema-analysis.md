# Schema analysis — turning the type list into an attack plan

The schema is the *full* attack surface — every field, every type, every
relationship. This file is the analysis workflow: how to read a schema dump
and produce a prioritized probe list. The output is a table: field → first
probe → expected harm.

---

## 1. The type inventory

```bash
# pull and classify
jq -r '.data.__schema.types[] | "\(.kind)\t\(.name)"' schema.json | sort
```

Count and bucket:

```text
OBJECT    — real types: User, Post, Order, Flag, Config...
ENUM      — value lists: Role{USER ADMIN}, Status{...}
INPUT_OBJECT — mutation arg shapes: RegisterInput, FilterInput
SCALAR    — String Int ID + custom: JSON, Upload, DateTime, Any
INTERFACE — Node, Entity, Resource — shared fields
UNION     — A | B | C — multi-type returns
```

**Immediately flag**: OBJECT types named for secrets —
`Flag`, `Secret`, `Config`, `Internal`, `Debug`, `Admin`, `Private`,
`Hidden`, `Backdoor`, `Token`, `Key`, `Credential`, `Session`, `Env`,
`Var`, `System`, `Health`, `Status`, `Info`, `Metrics`, `Stats`, `Log`,
`Audit`, `Event`, `Feature`, `Setting`, `Variable`, `Param`, `Property`.

## 2. The field-level read

Per type, every field's *return type* tells you its reach:

```graphql
type User {
  id: ID!
  username: String!
  email: String!          # private — high value
  role: Role!             # enum — privesc target
  token: String           # HIGH VALUE — auth material
  password: String        # plaintext-hash — HIGH VALUE
  apiKey: String          # HIGH VALUE
  sessions: [Session!]    # nested — session hijack
  posts: [Post!]          # list — mass read
  documents: [Document!]  # private docs — IDOR target
  orders: [Order!]        # financial — IDOR target
  profile: Profile        # nested — authz escape
  settings: Settings      # nested — config leak
}
```

**Field priority by return-type content:**

| Returns | Priority |
|---|---|
| `String` containing `flag|secret|token|key|password|hash|cred|jwt|api` | P0 |
| `Session`, `Token`, `Auth`, `Credential` types | P0 |
| `Config`, `Env`, `Settings`, `Vars` | P0 |
| `File`, `Document`, `Upload`, `Media`, `Asset` | P1 (file contents) |
| `User`/`Account`/`Profile` | P1 (PII) |
| `Order`, `Payment`, `Invoice`, `Balance` | P1 (financial) |
| `Log`, `Audit`, `Event`, `History` | P1 (internal ops) |
| `String` generically | P2 |
| `Int`, `Boolean`, `DateTime` | P3 |
| `[T]` list | same priority as T but mass-readable |

## 3. The argument-level read

```graphql
type Query {
  user(id: ID!): User               # IDOR surface
  users: [User!]                    # mass-read surface
  search(q: String!): [SearchResult]  # injection surface
  filter(f: FilterInput): [User!]    # object-injection surface
  node(id: ID!): Node               # global IDOR — node-interface.md
  file(name: String!): File         # path traversal surface
  download(path: String!): File     # LFI surface
  readFile(path: String!): File     # LFI surface
  exec(cmd: String!): String        # CMDI surface
  run(command: String!): String     # CMDI surface
  debug(code: String!): String      # eval surface
  eval(expr: String!): String       # eval surface
  importData(url: String!): ImportResult  # SSRF surface
  fetchAvatar(url: String!): String       # SSRF surface
  proxy(target: String!): String          # SSRF surface
}
```

**Argument-name → attack map:**

| Arg name | Bug class |
|---|---|
| `id`, `userId`, `user_id`, `uid`, `pk` | IDOR |
| `name`, `username`, `email`, `q`, `query`, `search`, `filter`, `where` | SQLi/NoSQLi |
| `filter`, `opts`, `options`, `params` (input object) | NoSQLi / mass-assign |
| `path`, `file`, `filename`, `name`, `dir` | LFI/traversal |
| `url`, `uri`, `target`, `dest`, `host`, `endpoint`, `callback` | SSRF |
| `cmd`, `command`, `code`, `expr`, `script`, `fn`, `eval` | CMDI/eval |
| `sort`, `order`, `orderBy`, `direction` | ORDER BY injection |
| `limit`, `offset`, `first`, `last`, `after`, `before` | pagination abuse |
| `role`, `type`, `kind`, `mode`, `level` | authz/enum tricks |
| `token`, `key`, `apiKey`, `secret`, `password`, `code`, `hash` | credential oracle |
| `data`, `input`, `doc`, `payload`, `body` | mass-assign |
| `width`, `height`, `size`, `format`, `quality` | image-proc cmdi |
| `x`, `y`, `lat`, `lon`, `zoom` | geo/indexed |
| `include`, `fields`, `select`, `attrs` | field-selection tricks |

## 4. The relationship map — where authz lives

```graphql
type Post {
  id: ID!
  title: String!
  author: User!         # Post → User edge — authz escape path
}
type User {
  posts: [Post!]        # User → Post edge
  email: String!        # private field on User
}
```

**Rule**: every edge `A.field → B` is a path to B that *may* skip B's own
entry-point authz. Build the graph:

```bash
# extract every OBJECT field that returns another OBJECT — the edges
jq -r '.data.__schema.types[] | select(.kind=="OBJECT") |
  .name as $t | .fields[] | select(.type.kind=="OBJECT" or
    (.type.kind=="NON_NULL" and .type.ofType.kind=="OBJECT") or
    (.type.kind=="LIST" and .type.ofType.kind=="OBJECT")) |
    "\($t).\(.name) -> \(.type.name // .type.ofType.name // "?")"' schema.json
```

Each edge is an authz-escape candidate — `post.author{email}` reaches
`User.email` without going through `user(id)`'s check.

## 5. The mutation map

```bash
jq -r '.data.__schema.types[] | select(.name=="Mutation").fields[] |
  "\(.name)(\([.args[] | .name + ":" + (.type.name // .type.ofType.name)] | join(", "))) -> \(.type.name // .type.ofType.name)"' schema.json
```

Classify each mutation:

```text
create*/register*/add*     → mass-assign surface; input-fields are the keys
update*/edit*/set*/change* → write-IDOR + mass-assign
delete*/remove*            → write-IDOR; destructive — probe on own objects
login*/auth*/signin*       → credential + JWT issues; batching attack
logout*                    → session-invalidation test
*Role/grant*/promote*      → privesc surface
upload*/import*/attach*    → file-upload surface
invite*/share*             → access-boundary writes
transfer*/pay*/checkout*   → logic/race
exec*/run*/debug*/eval*    → RCE surface
send*/notify*/email*       → message-injection → stored XSS/SSRF
verify*/confirm*/otp*      → brute-force via alias
reset*/forgot*             → user-enum + token-predictable
backup*/export*/dump*      → data-leak surface
system*/internal*/debug*   → admin surface
```

## 6. The input-object map — where mass-assign lives

```bash
jq -r '.data.__schema.types[] | select(.kind=="INPUT_OBJECT") |
  "\(.name): \([.inputFields[].name] | join(", "))"' schema.json
```

For each input object, the fields are the *keys the resolver accepts*:

```text
RegisterInput: username, password, email, role, isAdmin, verified
                                    ↑     ↑        ↑
                              the extras — mass-assign
```

Compare against what the front-end *sends*: `grep "registerInput\|input:"`
the bundle for the actual key list — the schema's extras are the
mass-assign targets.

## 7. The enum map — hidden values

```bash
jq -r '.data.__schema.types[] | select(.kind=="ENUM") |
  "\(.name): \([.enumValues[].name] | join(", "))"' schema.json
```

```text
Role: USER, ADMIN, SUPER_ADMIN, STAFF, MODERATOR, SUPPORT, BOT, SYSTEM
Status: ACTIVE, SUSPENDED, BANNED, PENDING, VERIFIED, DELETED
Plan: FREE, PRO, ENTERPRISE, ADMIN, INTERNAL
```

Enum values name the privesc targets — `role:"SUPER_ADMIN"` in a mass-assign,
`status:"VERIFIED"` in an update. The enum is the wordlist for the arg.

## 8. The custom-scalar map — free-form carriers

```text
SCALAR: JSON, JSONB, Any, Object, Map, Upload, DateTime, Email, URL, UUID, Decimal
```

Every field/arg typed `JSON`/`Any`/`Object`/`Map` is a raw-JSON carrier —
object injection, prototype pollution, operator smuggling all flow through
these without GraphQL string parsing touching them.

`Upload` scalars mark the multipart surface — `file-upload-graphql.md`.

## 9. The directive map — where authz is declared

```bash
jq -r '.data.__schema.directives[] | "\(.name) @\(.locations|join(","))"' schema.json
```

`@auth`, `@hasRole`, `@isAuthenticated`, `@guard`, `@can`, `@middleware` —
the declared authz. Fields *without* them but returning private types are
the unguarded surface. Fields *with* them are only as strong as the directive
implementation — probe anyway (dead-directive pattern).

## 10. The surfaced map — the attack table

Build the final table:

```text
Field                     Path            Bug-class      Module
──────────────────────────────────────────────────────────────────
user(id:ID!)              /graphql        IDOR           idor-graphql.md
users                     /graphql        mass-read      idor-graphql.md
user(id:).email           /graphql        field-authz    authz-bypass.md
post.author.email         /graphql        nested-escape  authz-bypass.md
node(id:ID!)              /graphql        node-IDOR      node-interface.md
search(q:String!)         /graphql        SQLi           injection-graphql.md
filter(f:FilterInput)     /graphql        NoSQLi         injection-graphql.md
download(path:String!)    /graphql        LFI            injection-graphql.md
importData(url:String!)   /graphql        SSRF           injection-graphql.md
register(input:)          /graphql        mass-assign    mutation-abuse.md
updateUserRole(...)       /graphql        privesc        mutation-abuse.md
upload(file:Upload!)      /graphql        upload         file-upload-graphql.md
messageAdded              ws://...        subscription   subscriptions.md
flag(token:String!)       /graphql        token-gate     workflow.md §B
```

That table is the work plan. Each row gets one `pre-probe` + `post-probe`
through the ledger.
