# Key check — the keyed-vs-unkeyed determination, in one place

The complete key check — the send-then-clean-request test.

---

## 1. The key check — is the input keyed

```bash
# the keyed-vs-unkeyed check — send the input → check the stored copy
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected → unkeyed → poisonable; NOT reflected → keyed → a different class
```

## 2. The keyed result — a per-input entry

```text
a keyed input → a per-input entry → YOUR input's effect is in YOUR
copy only → a different requester gets a different key → the clean
request doesn't reflect → a different class.
```

## 3. The unkeyed result — a shared entry

```text
an unkeyed input → a shared entry → the stored copy carries YOUR
input's effect → every requester's copy serves it → the clean request
reflects → poisonable.
```

## 4. The Vary check — the keyed-header check

```bash
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: X-Custom → the cache keys on X-Custom → a keyed header
#   (no Vary) → the cache ignores the headers → a shared entry
```

## 5. The key-source check — the configured key

```bash
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|hash_data|make_cache_key' <src> | head -10
#   $uri → the params unkeyed; $request_uri → the params keyed
#   a hash_data(req.http.X-Forwarded-Host) → that header keyed
```

## 6. The per-request-part key-check — the complete table

```text
request part              keyed?                    the check
the URL (path+query)      yes (the default key)     — always keyed
a Vary'd header           yes                       — the Vary names it
an unkeyed header         no                        → the input vector
a query param             yes (in $request_uri)     — usually keyed
                          no (if stripped)          → the param vector
the Host                  yes (in $proxy_host)      — usually keyed
                          no (if ignored)           → the host vector
the method                yes (GET vs POST)         — usually keyed
the cookie                yes (if Vary: Cookie)     — per-session entries
                          no (if unkeyed)           → the cookie vector
the auth state            yes (if Vary/keyed)       — per-session entries
                          no (if unkeyed)           → the deception vector
```

## 7. The key-check's falsifier — when nothing is unkeyed

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class.
```

## 8. The key-check's edge — a cache-buster

```bash
# a keyed param the app ignores — a cache-buster
curl "$BASE/page?cb=<unique>&_=<random>" -H 'X-Forwarded-Host: <marker>'
# the stored copy is keyed per-_ — a fresh entry, not a poisoned one
```

## 9. The key-check's confirm — the two-request test

```bash
# the store+serve check — the second request's HIT
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # first — MISS
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # second — HIT?
#   a HIT → the stored copy served it
```

## 10. The key-check's ledger — what to record

```bash
python3 tools/state.py <c> --hypothesis \
  "cache-poison-key-check: input=<unkeyed> — key=<cached-parts> — hit=<yes>"
```
