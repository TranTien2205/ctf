# Detection — finding and fingerprinting the GraphQL surface

Everything downstream depends on one thing first: proving the endpoint is
GraphQL and learning which server library answers it. This file covers the
recognition surface — where endpoints hide, what a GraphQL response looks like,
how to fingerprint the engine, and what each engine implies for attack surface.

The proof standard applies here too: a route named `/graphql` is a *candidate*.
The class is only live once the endpoint answers a query document with the
GraphQL response shape (`data`, `errors`, `extensions` keys), or rejects it
with a GraphQL validation error.

---

## 1. Where endpoints live

GraphQL endpoints are deliberately boring paths. The enumeration list, ordered
by hit frequency observed across targets:

```text
/graphql
/api/graphql
/graphql/v1
/v1/graphql
/api
/query
/gql
/api/gql
/graphql/console
/graphiql            ← the IDE, but often mounted next to the endpoint
/playground          ← Apollo Playground
/altair              ← Altair client
/voyager             ← schema visualiser
/graphql-explorer
/console             ← Hasura console
/api/v2/graphql
/graphql-devtools
/_graphql
/admin/graphql
/internal/graphql
/api/query
```

Trailing detail that matters:

- Many frameworks mount the endpoint at the API root itself (`/api` answers a
  query document). If `/api` 404s on a plain GET but is documented in the JS
  bundle, POST a query there.
- Versioned paths are common on mobile backends: `/v3/graphql`, `/2024-01/graphql`.
- Hasura conventionally serves `/v1/graphql` with the console at `/console`.
- Federation gateways listen at `/graphql` while subgraphs sit behind — the
  gateway is the reachable surface, subgraph routes like `/graphql/users` may
  also be exposed on some dev setups.

Find the endpoint in the bundle before guessing:

```bash
python3 tools/web/bundle_miner.py --url https://$HOST/ --out /tmp/bundle
grep -rE "graphql|gql|/query|apollo|relay|urql" /tmp/bundle | head -40
```

`bundle_miner` already ranks `graphql|gql` paths as interesting relative paths —
check its endpoint inventory first.

A registration of the client in the JS also names the endpoint verbatim:

```js
new ApolloClient({ uri: "/graphql", cache: new InMemoryCache() })
createClient({ url: "https://api.acme.tld/graphql" })        // urql
new Relay.Environment({ network: fetchFn("/api/graphql") })
```

## 2. Recognition signals — HTTP shape

A route is GraphQL when:

- **POST + JSON body containing a `query` key** returns 200 with a JSON object
  holding `data` and/or `errors`.
- **GET with `?query={__typename}`** returns `{"data":{"__typename":"Query"}}`.
- A nonsense query returns a *GraphQL-shaped* error — an `errors` array whose
  entries have `message`, `locations` (`line`, `column`), and often `path`:

```json
{"errors":[{"message":"Cannot query field \"nope\" on type \"Query\".",
  "locations":[{"line":1,"column":3}]}]}
```

That error shape alone confirms the parser ran — which confirms GraphQL even
when `data` is null.

- `Content-Type` handling: the endpoint accepts
  `application/json`, often `application/graphql` (raw document in body), and
  sometimes `application/x-www-form-urlencoded` with `query=...` — the last is
  the CSRF-relevant carrier, see `csrf-graphql.md`.

## 3. The minimal probe pair

Two requests discriminate "GraphQL" from "REST that happens to parse JSON":

```bash
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  --data-binary '{"query":"{__typename}"}'
# → {"data":{"__typename":"Query"}}  confirms

curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  --data-binary '{"query":"{definitelyNotAField}"}'
# → {"errors":[{"message":"Cannot query field ..."}]}  also confirms
```

Either response shape proves the endpoint parses GraphQL documents. If both
return a generic framework 404/400 page (`<html>` body, `Whitelabel Error
Page`, Django debug HTML), the route is probably not GraphQL — record the
negative and move on.

With the repository tools:

```bash
python3 tools/web/http_probe.py --challenge $CHAL --url "$BASE/graphql" \
  --body '{"query":"{__typename}"}' --header 'Content-Type: application/json'
```

`http_probe` emits the full `post-probe` command with `--response` filled —
use it rather than pasting.

## 4. Engine fingerprinting

Different servers leak themselves through errors, headers, and IDE defaults.
The fingerprint decides which deep file applies.

| Signal in response / behaviour | Engine guess |
|---|---|
| `Server: apollo-server` or `x-powered-by: Express` + `/graphql` | Apollo Server (Node) |
| Errors include `"extensions":{"code":"BAD_USER_INPUT","stacktrace":[...]}` | Apollo Server ≥3 |
| Error has `"code": "INTERNAL_SERVER_ERROR"` + `stacktrace` array in dev | Apollo dev mode |
| Playground at `/graphql` on GET with HTML | Apollo Server ≤2 / graphql-playground |
| GraphiQL at `/graphiql` | express-graphql / graphene / most libs |
| Errors list `"did you mean"` suggestions | graphql-js reference implementation and descendants |
| `"syntax error"` phrasing `Syntax Error: Expected Name, found ...` | graphql-js |
| `X-Powered-By: graphene` or `Django` headers + `/graphql` | Graphene-Django (Python) |
| `/v1/graphql` + `x-hasura-*` response headers | Hasura (see `hasura.md`) |
| `_service{sdl}` resolves | Apollo Federation (see `federation.md`) |
| `_entities` or `_any` root field | Federation subgraph |
| Errors like `{"errors":[{"message":"Unexpected end of document","extensions":{"category":"graphql"}}]}` | Sangria (Scala) or a strict lib |
| PHP stack + Lighthouse config references | lighthouse-laravel |
| `.net` + `GraphQL.Server` package + banana-cake-pop IDE | HotChocolate (.NET) |
| Ruby stack + `/graphql` POST-only | graphql-ruby |
| Elixir/Phoenix + Absinthe debug header | Absinthe |
| Rust `async-graphql` styled errors | async-graphql / Juniper |
| Juniper: errors mention `field "x" not found in type` | Juniper |
| `hasura` in `server` header, `extensions.path` in errors | Hasura |
| Error message contains `exception` and `code` objects | graphql-java |
| `PersistedQueryNotFound` error text | Apollo persisted-query support |
| `OperationName` required errors | strict operation-name policy |

Fingerprint probe batch (one request each; record each response):

```bash
# 1. malformed syntax — leaks parser identity
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d '{"query":"{"}'

# 2. unknown field — leaks suggestion oracle
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d '{"query":"{__typenaam}"}'

# 3. IDE discovery
curl -s -o /dev/null -w '%{http_code} %{url_effective}\n' "$BASE/graphiql"
curl -s -o /dev/null -w '%{http_code}\n' "$BASE/graphql" -H 'Accept: text/html'

# 4. federation markers
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{_service{sdl}}"}'
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{__schema{queryType{fields{name}}}}"}' | head -c 2000
```

The malformed-document error is the most reliable engine tell: every library
has its own error-string grammar.

## 5. Server-version leaks

- Apollo dev mode returns stack traces in `extensions.stacktrace` — the file
  paths inside leak the deployment layout (`/app/node_modules/...`).
- graphql-playground's HTML contains the endpoint URL it targets — check for
  internal hosts the browser build never mentions.
- Hasura errors carry `extensions.internal` in dev — stack + SQL statement.
- Django debug (`DEBUG=True`) turns resolver exceptions into full tracebacks
  inside the GraphQL `errors` entries — a free source-path disclosure.
- graphql-java’s `ExceptionWhileDataFetching` wraps the Java exception class
  name — e.g. `SqlExceptionHelper` leaks Hibernate.

Record every leak verbatim — each is potential `post-probe --evidence`.

## 6. Transports the endpoint accepts

Probe all three; a permissive transport is itself an attack surface
(`csrf-graphql.md`, `request-shapes`):

```bash
# form-encoded — relevant for CSRF and content-type confusion
curl -s "$BASE/graphql" -d 'query={__typename}'

# GET — relevant for CSRF and cache tricks
curl -s "$BASE/graphql?query=%7B__typename%7D"

# application/graphql — raw document
curl -s "$BASE/graphql" -H 'Content-Type: application/graphql' -d '{__typename}'

# batched array — see batching-attacks.md
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -d '[{"query":"{__typename}"},{"query":"{__typename}"}]'
```

Record which transports answer. A POST-only endpoint that rejects
`application/x-www-form-urlencoded` is harder to CSRF; a GET-accepting one is
trivially CSRF-able for queries (mutations over GET are rejected by spec but
many servers do not check).

## 7. Auth context detection

Determine whether introspection runs *before* or *after* authentication:

```bash
# unauthenticated
curl -s "$BASE/graphql" -d '{"query":"{__typename}"}' -H 'Content-Type: application/json'
# authenticated
curl -s "$BASE/graphql" -d '{"query":"{__typename}"}' -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN"
```

Divergence tells you the middleware order:

- Same answer both ways → schema introspection is unauthenticated (common).
- `401` unauth + `200` auth → auth middleware wraps the endpoint; the whole
  attack surface needs a session. Then test whether weak sessions (registered
  user) see the same schema as admin — per-resolver authz often differs.
- `200` unauth but a restricted type set → schema filtering by role — record
  which types appear only when authenticated; then hunt the resolvers that
  forget their own check (`authz-bypass.md`).

## 8. First negatives to record

`post-probe` these so the next agent does not re-walk them:

| Observation | Verdict |
|---|---|
| `?query={__typename}` → framework 404 | route is not graphql — class closed |
| POST `{"query":"{__typename}"}` → `{"errors":[...Cannot query field "__typename"...]}` | non-graphql parser that happens to accept JSON — closed |
| introspection error `GraphQL introspection is not allowed` | introspection channel closed; `introspection-off.md` opens |
| All transports except POST+JSON rejected | CSRF window narrows; record |
| `{"data":{"__typename":"Query"}}` but every field errors `not authorized` | authz-per-resolver in force — go to `authz-bypass.md` |

Ledger writes:

```bash
python3 tools/state.py $CHAL --bug-class web-graphql
python3 tools/state.py $CHAL --hypothesis "endpoint accepts unauthenticated introspection"
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {"query":"{__typename}"}' \
  --verdict confirms --evidence-kind class --class web-graphql \
  --hypothesis-id h1 --evidence '{"data":{"__typename":"Query"}}' \
  --response '<raw body>'
```

## 9. Do NOT confuse with

| Look-alike | Discriminator |
|---|---|
| REST `/api` accepting JSON | no `query` document key; errors not in `{message,locations}` shape |
| A generic "query DSL" endpoint | `{__typename}` errors "unexpected character" not "Cannot query field" |
| SQL-over-HTTP (OData, RESTheart) | `$filter`/`$select` params, not a document |
| JSON-RPC | `{"jsonrpc":"2.0","method":...}` envelope |
| SOAP | XML body, `soap:Envelope` |

The one-line discriminator is always `{__typename}` — every spec-compliant
server answers it; nothing else does.
