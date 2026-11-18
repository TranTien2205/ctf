# GraphQL over HTTP — the transport contract

The spec is loose about HTTP — implementations disagree on methods, content
types, status codes, and body shapes. The disagreements *are* the attack
surface: each accepted variant is a different parser and a different
middleware path. This file is the transport grammar.

---

## 1. Method accept matrix

| Method | Spec | Reality |
|---|---|---|
| POST | required | universal |
| GET | allowed for queries | most servers; mutations SHOULD be rejected (often aren't) |
| PUT/PATCH/DELETE | unspecified | some frameworks pass to the same handler |
| OPTIONS | CORS preflight | must not execute — check |
| HEAD | like GET | some servers execute! |

Probe every method — an unexpected method answering a query is a middleware
gap:

```bash
for m in GET POST PUT PATCH OPTIONS HEAD; do
  code=$(curl -s -o /tmp/o -w '%{http_code}' -X $m "$BASE/graphql" \
    -H 'Content-Type: application/json' -d '{"query":"{__typename}"}')
  echo "$m → $code $(head -c80 /tmp/o)"
done
```

`HEAD` executing is the sneaky one — the response body is empty but the
resolver **ran**; a `HEAD` mutation would execute with no response body to
inspect — a write that can't be read, but still a write.

## 2. Body-shape matrix

```bash
# canonical
POST {"query":"{x}","variables":{},"operationName":"Op"}

# minimal
POST {"query":"{x}"}

# array batch
POST [{"query":"{x}"},{"query":"{y}"}]

# bare string — some lenient servers accept
POST "{x}"

# nested under a key — REST-wrap shapes
POST {"data":{"query":"{x}"}}
POST {"graphql":{"query":"{x}"}}
POST {"request":{"query":"{x}","variables":{}}}

# duplicated keys — parser differential
POST {"query":"{x}","query":"{y}"}
```

The duplicated-key probe: which `query` wins — first, last, or both-joined?
Different JSON parsers pick differently → `skills/web-parser-differential/`.

## 3. Content-Type matrix

```bash
application/json                          # canonical
application/json; charset=utf-8
application/graphql                       # raw document
application/graphql+json                  # new spec CT
application/x-www-form-urlencoded         # query=...&variables=...
text/plain                                # simple-request bypass
multipart/form-data                       # upload spec
application/octet-stream                  # some accept raw
```

Each accepted CT is a CSRF/WAF-relevant transport — `csrf-graphql.md`,
`waf-bypass.md`.

## 4. The variables field — second parser

`variables` is a JSON *object* — parsed by the JSON layer, **not** the
GraphQL parser. That split is exploitable:

```json
{"query":"query($id:ID){user(id:$id){id}}",
 "variables":{"id":{"$ne":null}}}
```

The object value passes JSON validation; the GraphQL validator should reject
it — but lax validators pass it through → `type-confusion.md`.

Variables can also arrive as a *string-encoded* JSON in form posts:

```
query=query($id:ID){user(id:$id){id}}&variables={"id":"1"}
```

Some servers expect the string; others the object; a lax one accepts either.
Double-encoded `variables="%7B%22id%22%3A%221%22%7D"` gives a third parser
variant — probe all three.

## 5. operationName games

```json
{"operationName":"Login","query":"mutation Login{...}"}
{"operationName":"Login","query":"query Other{...}"}   # mismatch!
{"operationName":"does-not-exist","query":"{x}"}
{"operationName":123,"query":"{x}"}                    # wrong type
{"operationName":["A","B"],"query":"{x}"}              # array
{"operationName":null,"query":"{x}"}
{"operationName":"A","query":"query A{x} query B{y}"}  # multi-op doc
```

- Multi-operation documents REQUIRE `operationName` to pick one — the
  *non-selected* op is validated but not executed. Authz keyed on the
  selected op may run both resolvers anyway on buggy servers.
- A WAF inspecting `operationName` for threat names can be fooled by
  renaming — the op name is cosmetic; the doc is what executes.

## 6. extensions — the free-form channel

```json
{"query":"{x}","extensions":{"anything":"goes","persistedQuery":{...},
  "tracing":true,"debug":1,"includeStacktrace":true}}
```

`extensions` is spec-free — servers read debug/trace/persisted-query flags
from it. Try:

- `{"extensions":{"debug":1,"trace":1}}` — dev-mode toggles.
- `{"extensions":{"persistedQuery":{...}}}` — APQ channel (`persisted-queries.md`).
- `{"extensions":{"ftv1":true}}` — Apollo federation trace.
- `{"extensions":{"includeException":true}}` — error detail toggle.
- Arbitrary keys — free-form smuggling channel into resolvers that read
  `context.extensions`.

## 7. Status-code semantics per implementation

| Impl | Validation error | Execution error | Success |
|---|---|---|---|
| graphql-js/express | 400 | 200+errors | 200 |
| Apollo ≥4 | 200 always | 200+errors | 200 |
| graphql-java | 200/400 mixed | 200 | 200 |
| Hasura | 200/400 | 200 | 200 |
| Sangria | 400 | 500 | 200 |
| graphene | 400 | 200+errors | 200 |

**Never trust status alone** — always read `data`/`errors` split. A 200 with
`errors` only is a validation pass + resolver failure; a 400 is a validation
fail; both matter differently.

## 8. Header games

```bash
# content negotiation — Accept: application/graphql-response+json (new spec)
# vs application/json — the server's negotiation reveals version
curl -s "$BASE/graphql" -H 'Accept: application/graphql-response+json' ...

# apollo headers
x-apollo-operation-name: X
apollo-require-preflight: true          # csrf-protection toggle in Apollo 4
x-apollo-federation-include-trace: ftv1

# graphql-ws over HTTP — some servers multiplex
Sec-WebSocket-Protocol: graphql-transport-ws

# debug toggles
x-graphql-debug: 1
x-graphql-tracing: 1
```

`apollo-require-preflight` — Apollo 4's CSRF protection header: requests
*without* it get rejected IF enabled. Its absence→acceptance proves CSRF
protection is off.

## 9. Batched transport acceptance detection

```bash
# one probe — array vs object discrimination
curl -s "$BASE/graphql" -d '[{"query":"{__typename}"}]' ...
# array response → batching on; object error → off
```

Also **GET-batched**: `?query=[{...},{...}]` — some accept arrays in the GET
param too.

## 10. Recording

The transport matrix is reusable intel — record it once:

```bash
python3 tools/state.py $CHAL --hypothesis \
  "accepts: POST+JSON, form-urlencoded, GET; rejects text/plain; batching on"
```

Every downstream exploit picks the cheapest accepted transport — the matrix
tells it which.
