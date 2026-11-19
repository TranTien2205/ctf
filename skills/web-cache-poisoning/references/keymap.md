# Keymap — the cache key's complete map, exhaustively

Every request part, whether it's in the key, and the check.

---

## 1. The default key — the URL+method

```text
the default cache key = the URL (scheme + host + path + query) + the
method. headers are unkeyed UNLESS the config adds them or the
response carries Vary. a Vary header names the request headers that
vary the stored entry.
```

## 2. The Vary header — the key's discriminator

```bash
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie — the cache keys on the cookie → per-session entries
#   Vary: Accept-Encoding — the cache keys on the encoding → per-encoding entries
#   Vary: Authorization — the cache keys on auth → per-auth entries
#   Vary: X-Custom — the cache keys on X-Custom → a keyed header
#   (no Vary) — the cache ignores those headers → a shared entry
```

## 3. The proxy_cache_key template — the configured key

```nginx
proxy_cache_key $scheme$proxy_host$request_uri;   # the URL (scheme+host+URI)
proxy_cache_key $scheme$proxy_host$request_uri$http_x_custom;  # + a keyed header
proxy_cache_key $scheme$proxy_host$request_uri$arg_cb;         # + a keyed param
proxy_cache_key $scheme$proxy_host$uri;           # $uri drops the query → unkeyed params
```

## 4. The vcl_hash — the Varnish key

```vcl
sub vcl_hash {
  hash_data(req.url);
  hash_data(req.http.Host);
  # a header NOT hashed is unkeyed
}
```

## 5. The per-request-part keymap — the complete table

```text
request part              keyed?                    the check
the URL (path+query)      yes (the default key)     — always keyed
a Vary'd header           yes                       — the Vary names it
an unkeyed header         no                        → the input vector
a query param             yes (in $request_uri)     — usually keyed
                          no (if stripped/$uri)     → the param vector
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

## 6. The keyed-vs-unkeyed check — is it really unkeyed

```bash
# send the input → check the stored copy serves it to a clean request
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # store it
curl "$BASE/page?cb=<unique>"   # a clean request — does it reflect <marker>?
#   reflected → unkeyed → poisonable; NOT reflected → keyed → a different class
```

## 7. The keymap's falsifier — when nothing is unkeyed

```text
every candidate input IS keyed → no unkeyed input → no poisoning
vector → a different class. the whole attack depends on a request
part the app reads but the cache ignores — none means a different
class.
```

## 8. The keymap's use — the poisoning vector

```text
the unkeyed input is the poisoning vector — the request part the app
reads but the cache ignores — the stored copy carries its effect to
every requester.
```
