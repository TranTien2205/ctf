# Framework and engine notes — per-implementation quirks

Each GraphQL implementation has its own defaults, its own error grammar, its
own middleware story. This file is the per-engine playbook — the fingerprint
signals, the default-open surfaces, and the version-specific bugs.

---

## 1. Apollo Server (Node.js)

**Fingerprint**: `extensions.code` taxonomy (`BAD_USER_INPUT`,
`INTERNAL_SERVER_ERROR`, `UNAUTHENTICATED`), `stacktrace` arrays in dev,
`x-powered-by: Express`, Playground landing page on GET in dev.

**Defaults that matter:**

- **Apollo ≤3**: introspection on in dev, **off in prod** (`NODE_ENV=production`
  flips it). Playground always on in dev. `landingPage` plugin controls it.
- **Apollo 4**: `csrfPrevention` option — when ON, rejects requests missing
  `Apollo-Require-Preflight` or non-simple CTs. When OFF (default),
  form-urlencoded/GET mutations go through → CSRF.
- **`allowBatchedHttpRequests`** — v3 on by default, v4 gated. Array batching.
- **Error masking**: `formatError` hook can strip details; `debug: true` in
  extensions re-enables stacktraces on some configs.
- **`includeStacktraceInErrorResponses`** — dev default true.

**Probes**:

```bash
# CSRF-protection detection
curl -s "$BASE/graphql" -H 'Content-Type: text/plain' -d '{"query":"{x}"}'
# 400 "This operation has been blocked as a potential CSRF" → prevention ON

# landing page
curl -s "$BASE/graphql" -H 'Accept: text/html' | grep -i 'apollo\|playground\|landing'

# stacktrace force
curl -s "$BASE/graphql" -d '{"query":"{x}","extensions":{"debug":1}}' ...
```

**Known version bugs**: Apollo ≤2 introspection always on; `graphql-tools`
mock mode leaks; `@apollo/gateway` `_service` leakage. Plugin ecosystem —
`graphql-depth-limit` often added but shallow defaults.

## 2. express-graphql (legacy reference impl)

**Fingerprint**: `Syntax Error:` errors, `did you mean` suggestions always on,
GraphiQL at `?graphiql`, the OLDEST error grammar (pre-extensions).

**Defaults**: introspection always on (no off switch except middleware), no
auth built-in, accepts GET+POST+form+JSON, executes mutations over GET
(spec violation!). `graphiql:true` in dev.

```bash
# mutation over GET — express-graphql allows it
curl -s "$BASE/graphql?query=mutation{deleteAll}"
```

## 3. graphql-yoga

**Fingerprint**: yoga's `extensions` shape, `Accept: text/event-stream` for
subscriptions, default landing page.

**Defaults**: introspection on, GraphiQL on `/graphql` GET+Accept:html,
`maskedErrors` on in prod (generic "Unexpected error.") — but **suggestion
oracle still on**. Multipart upload support built-in.

```bash
# masked-error bypass via suggestion oracle — still answers
curl -s "$BASE/graphql" -d '{"query":"{userrs}"}'
# → "Did you mean \"users\"?" even when other errors are masked
```

## 4. Graphene-Django (Python)

**Fingerprint**: `errors[].locations`, graphene-style `Cannot query field`,
Django headers (`X-Frame-Options: DENY`, `csrftoken` cookie), `/graphql` POST.

**Defaults**: introspection ON, `graphene_django` middleware, CSRF exempt
by default on the view (Django `csrf_exempt` wrapper common!), file upload
via `graphene-file-upload` (multipart spec), Relay `node` via `relay.Node`.

**Django-specific**:

- `CSRF_EXEMPT` commonly applied → CSRF-able.
- `DEBUG=True` → tracebacks inside errors.
- Relay `toGlobalId` → `base64("TypeName:pk")` — `node-interface.md` applies.
- `filters` via `DjangoFilterConnectionField` — `filter` args reach
  `filterset` classes → injectable per-field.
- `graphene-django-cud` mutations — `input` fields map to model fields →
  mass assignment.

## 5. Hasura

**Fingerprint**: `/v1/graphql`, `x-hasura-*` headers, `errors[].extensions.path`,
`extensions.internal` in dev, admin-secret header auth model.

**Defaults**: introspection on unless `HASURA_GRAPHQL_DISABLE_INTROSPECTION`,
**role-based schema filtering** — `x-hasura-role: anonymous` shows a
different schema than `admin`. `x-hasura-admin-secret` header = god-mode.

**The Hasura authz model is different**: role-based permission *declarations*
on tables. Bugs live in:

- `x-hasura-role` **header spoofing** — if the auth webhook/JWT maps a role
  that shouldn't be assignable, or no webhook + admin secret needed:
  `x-hasura-role: admin` in the request.
- `x-hasura-user-id` trusted header — when the webhook is misconfigured.
- `default` role having read on tables admin didn't mean to share.
- `remote_schemas`/`actions` — proxying through Hasura's outbound HTTP →
  SSRF via `x-hasura-*` forwarded headers.
- `allow-list` — when set, only allowlisted queries run; a
  `x-hasura-admin-secret` leak unlocks the whole console.

```bash
# role spoofing
curl -s "$BASE/v1/graphql" -H 'x-hasura-role: admin' -d '...'
curl -s "$BASE/v1/graphql" -H 'x-hasura-admin-secret: x' -d '...'
curl -s "$BASE/console" -I  # console exposed?
```

Deep: `hasura.md`.

## 6. graphql-java / Spring Boot

**Fingerprint**: `errors[].extensions.classification`,
`ExceptionWhileDataFetching`, `Banana Cake Pop`/`GraphiQL` servlet, Java
exception class names in errors.

**Defaults**: introspection on, **no suggestion oracle**, `/graphql` servlet
path, multipart upload via `graphql-java-servlet`.

```bash
# java exception leak
{"errors":[{"message":"Exception while fetching data (/user) : ...",
  "extensions":{"classification":"DataFetchingException"},
  "exception":{"stackTrace":"java.sql.SQLSyntaxErrorException: ..."}}]}
```

The `exception` field carries raw Java stack — SQL, file paths, jar versions.

## 7. graphql-ruby

**Fingerprint**: `"Field 'x' doesn't exist on type 'Query'"` (no suggestions),
`extensions: {"code":"..."}`, Rails asset fingerprints.

**Defaults**: introspection on, `GraphiQL::Rails` at `/graphiql`, schema
`use GraphQL::Analysis::AST` for limits, mutations via `BaseMutation`, input
strictness *strict* (no extra keys by default).

**Ruby-side**: `devise`-backed auth context via `context[:current_user]`.
`Pundit`/`CanCanCan` policy checks inside resolvers — per-resolver authz is
the *only* enforcement; a missing `authorize` call is the bug.

## 8. Absinthe (Elixir/Phoenix)

**Fingerprint**: `Did you mean ...?` in errors, `extensions.code`,
Phoenix `x-request-id`, `/api` or `/graphiql` defaults.

**Defaults**: introspection on, `Absinthe.Plug` accepts GET+POST+multipart,
subscriptions over Phoenix Channels (not raw ws — needs `phoenix` socket
protocol), `__ABSINTHE_SCHEMA__` compile-time schema — schema is baked, not
runtime-mutable.

## 9. HotChocolate (.NET)

**Fingerprint**: `Banana Cake Pop` IDE, `.extensions.code` taxonomy,
`"Path"` + `"Locations"` capitalized fields, `AllowIntrospectionFields`
option.

**Defaults**: introspection on, **suggestion oracle on**, multipart upload,
subscriptions over WS, `[Authorize]` attribute per-resolver.

```bash
# HotChocolate's IDE
curl -s "$BASE/graphql/ui/bcp" -I
curl -s "$BASE/graphql" -H 'Accept: text/html'  # BCP auto-serve
```

## 10. Juniper / async-graphql (Rust)

**Fingerprint**: Juniper: `field "x" not found in type`; async-graphql:
`extensions.code`, `extensions.trace_id`. Axum/warp wrappers.

**Defaults**: introspection on, **strict typing** (extra input keys rejected),
subscriptions on WS, dataloaders for batching.

## 11. Mercurius (Fastify)

**Fingerprint**: fastify `x-response-time`, `errors[].extensions` with
`code`, Fastify headers. GraphiQL via `graphiql:true` option.

**Defaults**: introspection on, multipart upload off by default, query depth
limits via `queryDepthLimit` option, subscription on WS.

## 12. gqlgen (Go)

**Fingerprint**: `{"errors":[{"message":"...","path":["x"]}]`, `extensions`,
Go's `net/http` headers, playground at `/` or `/playground`.

**Defaults**: introspection on, multipart upload via `graphql-transport`,
complexity limits via `extension.FixedComplexityLimit`.

## 13. Lighthouse (PHP/Laravel)

**Fingerprint**: Laravel session cookies, `errors[].extensions` with
`category: "graphql"` or `"internal"`, `/graphql` POST.

**Defaults**: introspection on, `@guard`/`@can`/`@belongsTo`/`@hasMany`
directive-based authz+relations — the directive graph IS the schema.
`@middleware` directive wraps Laravel middleware — **declared on field but
skipped on some resolver paths**.

## 14. PostGraphile (Postgres → auto-GraphQL)

**Fingerprint**: Postgres-flavored errors, auto-generated naming
(`allUsers`, `userById`, `userByUsername`, `updateUser`, `deleteUser`),
`x-graphql-total-count` headers, `natural sort` enum.

**Defaults**: introspection on, RLS (row-level security) does authz at the
DB layer — the *only* authz is Postgres's own. `pg_settings` role spoofing:

```graphql
# RLS via JWT claims — a weak JWT secret = full impersonation
# → skills/web-auth-session/ for the JWT attack
```

`allX` list fields are the IDOR surface — `allUsers`, `allOrders` return
*everything the RLS role can see* — the bug is RLS misconfig, not GraphQL.

## 15. Strawberry (Python)

**Fingerprint**: Graphene-sibling API, `errors[].extensions`, newer stacks.
Defaults: introspection on, multipart upload, subscriptions over ASGI-WS.

## 16. Atlas/Magento/JWP — the embedded GraphQLs

Products that ship GraphQL as a secondary API:

- **Magento**: `/graphql` full storefront — `customer`, `products`, cart
  mutations; the `store` header selects the store view; `allProducts` IDOR.
- **Wordpress WPGraphQL**: `/graphql` plugin — `posts`, `users`,
  `generalSettings` — settings leak siteurl/admin paths.
- **Ghost**: `/-/graphql` admin API — members/posts/staff.
- **Dgraph**: `/graphql` native — query+DQL-in-GraphQL mix; `@auth` directive.
- **Supabase/postgREST**: NOT graphql — `pg_graphql` extension adds it at
  `/graphql/v1` — RLS controls all.

## 17. The cross-framework cheat

Whatever the engine, these probes are universal:

```graphql
{__typename}                       # engine detection
{_service{sdl}}                    # federation
{_entities(representations:[]){}}  # federation entities
{__schema{queryType{fields{name}}}}  # introspection probe
{__type(name:"Query"){fields{name}}} # type-level introspection
{x}                                # suggestion oracle probe
{f(a:"\"")}                        # escaping probe
{f(a:1e308)}                       # numeric parser probe
mutation{__typename}               # mutation root exists
subscription{__typename}           # subscription root exists
```
