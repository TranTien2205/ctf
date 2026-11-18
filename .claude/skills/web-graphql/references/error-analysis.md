# Reading GraphQL errors — every error is an oracle

GraphQL's `errors` array is structured — `message`, `locations`, `path`,
`extensions` — and each component leaks. A good error read tells you the
engine, the schema, the authz boundary, the underlying driver, and whether
the resolver even ran. This file is the error-shape dictionary.

---

## 1. The errors array anatomy

```json
{"errors":[{
  "message":"Cannot query field \"userss\" on type \"Query\". Did you mean \"users\"?",
  "locations":[{"line":1,"column":3}],
  "path":["userss"],
  "extensions":{"code":"GRAPHQL_VALIDATION_FAILED","stacktrace":["..."]}
}],"data":null}
```

| Component | Leaks |
|---|---|
| `message` text | validator identity, field/type names, driver text, JS/Python/Java exception strings |
| `locations` | document-position grammar — confirms document parsed |
| `path` | which *executed* field errored — tells you the resolver ran (vs validation) |
| `extensions.code` | server's error taxonomy — `UNAUTHENTICATED`, `FORBIDDEN`, `BAD_USER_INPUT`, `INTERNAL_SERVER_ERROR` |
| `extensions.exception` / `stacktrace` | **full backend trace** — file paths, line numbers, library names, SQL fragments |
| `extensions.category` / `internal` | Hasura/Sangria internals |

## 2. Validation errors — pre-execution

Parser/validator ran, resolver did **not**. These leak *schema*:

| Message | Learned |
|---|---|
| `Cannot query field "X" on type "Query"` | X doesn't exist on Query |
| `... Did you mean "users", "user"?` | suggestions oracle — `introspection-off.md` |
| `Field "user" argument "id" of type "ID!" is required` | field exists + required arg name + type |
| `Field "user" of type "User" must have a selection of subfields` | field exists + returns object |
| `Expected type ID, found "x"` / `Int cannot represent...` | arg type leaked |
| `Unknown argument "foo" on field "user"` | field exists; valid arg names not leaked (try schema) |
| `Unknown type "X"` in fragment | type doesn't exist |
| `Fragment "F" cannot condition on non composite type` | field returns scalar not object |
| `Variable "$x" of required type "ID!" was not provided` | op-declared args |
| `Syntax Error: Expected Name, found ...` | document malformed — parser identity |

`Cannot query field` *on a different type name* leaks the parent type:
`Cannot query field "x" on type "AdminPanel"` — you learn `AdminPanel` exists.

## 3. Execution errors — resolver ran

These leak *backend* — `path` present means execution reached that field:

| Message | Learned |
|---|---|
| `Cannot return null for non-nullable field Query.user` | resolver returned null — object absent OR filtered |
| `User not found` / `NotFoundError` | application-level, field exists |
| `error authenticating user: invalid token` | authz shape — tells what it wants |
| `Forbidden` / `You do not have permission` | per-resolver authz present |
| `sqlite3.OperationalError`, `MySQL`, `psql`, `ORA-` | **SQL reached** — injectable arg confirmed |
| `MongoError`, `BSONError`, `Cast to ObjectId` | NoSQL reachable |
| `ENOENT`, `Is a directory`, `Permission denied` | filesystem reachable |
| `ECONNREFUSED`, `getaddrinfo ENOTFOUND`, `ETIMEDOUT` | outbound fetch — SSRF surface |
| `Command failed`, `sh:`, `/bin/`, `cmd.exe` | shell reachable |
| `TypeError: Cannot read properties of undefined` | JS backend + resolver crash |
| `KeyError`, `AttributeError` | Python backend |
| `NullPointerException`, `ClassCastException` | Java/.NET backend |
| `Maximum call stack`, `heap out of memory` | circular query reached the resolver |

`path` shows which *executed* field failed — `path:["user","author","email"]`
means `user` resolved, `author` resolved, `email` errored — the leak lives
three edges deep, which is the nested-resolver escape
(`authz-bypass.md` §2.3).

## 4. extensions — the under-read leak

```json
"extensions":{
  "code":"INTERNAL_SERVER_ERROR",
  "exception":{
    "name":"Error",
    "message":"connect ECONNREFUSED 10.0.4.12:6379",
    "stacktrace":["Error: connect ECONNREFUSED 10.0.4.12:6379",
      "at TCPConnectWrap.afterConnect [as oncomplete] (net.js:1141:16)",
      "at Object.resolve (/app/resolvers/user.js:42:11)",
      "at field.resolve (/app/node_modules/graphql/...)" ]
  }
}
```

Each element leaks:

- `ECONNREFUSED 10.0.4.12:6379` — **internal IP + port**: redis, mongo,
  internal service. → `skills/web-ssrf/` target intel.
- `/app/resolvers/user.js:42` — **deployment layout + file:line**.
- `/app/node_modules/graphql/` — engine + dependency tree.
- SQL fragments in `exception` — the built query shape for injection tuning.
- `exception.name` — driver/class identity: `JsonWebTokenError`,
  `CastError`, `ValidationError`, `SequelizeDatabaseError`.

Dev-mode servers always ship `stacktrace`; prod should strip it — its
presence is itself a misconfig finding (info-disclosure class).

## 5. Partial responses — `data` + `errors` together

```json
{"data":{"user":{"id":1,"email":null}},
 "errors":[{"message":"Forbidden","path":["user","email"]}]}
```

One field failed, siblings returned. This is **the** field-level authz
signature: `email` nulled + `path:["user","email"]` + `Forbidden` = the
field exists, the authz caught it, data withheld — the check is per-field.
Then hunt the *path* that reaches the same field through another edge
(`authz-bypass.md` §2.3).

Also: partial results on **aliases** — `a1` fails, `a2` succeeds — tells you
the authz is per-resolver-call, not per-document.

## 6. Status-code semantics — which layer failed

| HTTP | Shape | Meaning |
|---|---|---|
| 200 + `data` | clean execution | fields resolved |
| 200 + `data`+`errors` | partial | some fields denied/errored — read per-field |
| 200 + `errors` only | resolver errors | validation passed, resolvers threw |
| 400 + `errors` | document invalid | parser/validator rejected — schema oracle only |
| 400 generic (no `errors` array) | transport rejected | WAF/proxy block — not GraphQL |
| 401/403 | auth middleware | HTTP layer — get a session first |
| 404 | wrong path | route doesn't exist — detection.md |
| 405 | wrong method | transport only |
| 429 | rate limit | batching-attacks.md |
| 500 bare | resolver crash | could still have executed partially — check `errors` |
| 502/503 | upstream fail | backend dead — record and retry |

**Important**: Apollo >=4 returns `200` for validation errors too — never
trust status alone; read `data` vs `errors`.

## 7. Error-suppression patterns — when errors are generic

Hardened servers return `{"errors":[{"message":"Unexpected error."}]}` with
`extensions.code:INTERNAL_SERVER_ERROR` and no detail. Then:

- **Status vs length** still differ across guesses (`introspection-off.md` §3).
- **`path` presence** still distinguishes validation vs execution.
- **Timing** still distinguishes branches (`blind-graphql.md`).
- Dev endpoints/modes may still leak — try `x-apollo-debug: 1`,
  `?debug=1`, staging routes.

## 8. Probes that deliberately induce errors

```graphql
{x}                                 # syntax leak — parser identity
{__typename:42}                     # alias-as-int — validator grammar
{user(id:"\"")}                     # quote probe — driver text
{user(id:1/0)}                      # arithmetic — validator strictness
mutation{__typename}                # mutation-root exists?
subscription{__typename}            # subscription-root exists?
{... on Query{__typename}}          # fragment on root — some parsers reject
{x:__type(name:"Query"){name}}      # __type alive?
{f(x:NaN)} {f(x:Infinity)}          # non-JSON numerics — parser lax?
```

Each error's *shape* is data. Record engine-identifying strings verbatim —
they're classification evidence.
