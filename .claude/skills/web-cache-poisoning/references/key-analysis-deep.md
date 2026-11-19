# Key analysis deep — the cache key's composition, exhaustively

Every request part, whether it's in the key, and the check.

---

## 1. The cache key's anatomy — what determines the stored entry

```text
the cache key = the set of request parts that determine which stored
copy serves a request:
- the URL (scheme + host + path + query — the default)
- the Vary'd headers (the headers named in Vary)
- the proxy_cache_key template (the configured key parts)
everything NOT in the key is an unkeyed input — the stored response
carries its effect to every requester.
```

## 2. The default key — the URL+method

```text
the default nginx proxy_cache_key is the URL (scheme + host + URI) —
headers are unkeyed UNLESS the config adds them or the response
carries Vary. a Vary header names the request headers that vary the
stored entry.
```

## 3. The Vary header — the key's discriminator

```bash
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie — the cache keys on the cookie → per-session entries
#   Vary: Accept-Encoding — the cache keys on the encoding →
#                          per-compression entries
#   Vary: Authorization — the cache keys on auth → per-auth entries
#   Vary: X-Custom — the cache keys on X-Custom → a keyed header
#   (no Vary) — the cache ignores those headers → a shared entry
```

```text
a Vary header names the request headers that determine the stored
entry — a header NOT in Vary is an unkeyed input — the stored
response serves YOUR input to every requester.
```

## 4. The proxy_cache_key template — the configured key

```nginx
# a typical nginx config — the key template
proxy_cache_key $scheme$proxy_host$request_uri;
#   the key = the scheme + the host + the URI — headers are unkeyed
proxy_cache_key $scheme$proxy_host$request_uri$http_x_custom;
#   the key includes $http_x_custom — that header IS keyed
proxy_cache_key $scheme$proxy_host$request_uri$arg_cb;
#   the key includes the cb param — that param IS keyed
```

## 5. The Varnish key — the vcl_hash builder

```vcl
# a Varnish config — the cache + the key
sub vcl_hash {
  hash_data(req.url);
  hash_data(req.http.Host);  # the host is keyed
  # a header NOT hashed is unkeyed
}
```

## 6. The key-buster — a keyed param the app ignores

```bash
# a cache-buster — a keyed param the app ignores
curl "$BASE/page?cb=<unique>&_=<random>"
#   the stored entry is keyed per-_ — a fresh entry, not a poisoned one
```

```text
a keyed param the app ignores keys the entry per-value — the stored
response is YOUR requests only — a cache-buster defeats the poisoning.
```

## 7. The keyed-vs-unkeyed check — is it really unkeyed

```bash
# send the input → check the stored copy serves it to a clean request
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   <marker> reflected → unkeyed → poisonable
#   <marker> NOT reflected → keyed → a different class
```

## 8. The authenticated-page key-check — the auth-state question

```text
the verified card's shape: an authenticated page cached under a URL
the anonymous requester also fetches — the cache keys on the URL,
not the auth state — the stored response is the privileged page.
the key question: does the cache key include the auth state? a
Vary: Cookie or a keyed session header keys the entry per-session;
an unkeyed URL serves the authenticated copy anonymously.
```

## 9. The per-request-part key-check — the complete table

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
a scheme header           yes (if in the key)       — usually keyed
                          no (if ignored)           → the scheme vector
the auth state            yes (if Vary/keyed)       — per-session entries
                          no (if unkeyed)           → the deception vector
```

## 10. The key-map — which inputs are poisonable

```bash
# for each candidate input — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Scheme' 'X-Forwarded-Server' 'X-Host'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## 11. The key's falsifier — when nothing is unkeyed

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class. the whole attack depends on a request
part the app reads but the cache ignores — none means a different
class.
```

## 12. The key's falsifier check — the cache-buster test

```bash
# a keyed param the app ignores — a fresh entry each value
curl "$BASE/page?cb=<unique>&_=<random>" -H 'X-Forwarded-Host: <marker>'
# the stored copy is keyed per-_ — a fresh entry, not a poisoned one
# a cache-buster defeats the poisoning — a keyed param isn't poisonable
```
