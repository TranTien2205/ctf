# Detection workflow — the cache-poisoning detection sequence, end to end

The step-by-step detection — the cache, the key, the unkeyed input, the confirm.

---

## Step 0 — the cache-status check — does a cache exist

```bash
# the cache status — a HIT/MISS/AGE header
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish|x-served-by|server'
#   X-Cache-Status: HIT/MISS — nginx; CF-Cache-Status — Cloudflare
```

```text
a cache-status header → a front-end cache exists. no status header
doesn't mean no cache — check the config anyway.
```

## Step 1 — the Vary check — what's keyed

```bash
# the Vary header — which headers vary the cache
curl -sI "$BASE/" | grep -i 'vary'
#   Vary: Cookie → keyed on the cookie; (no Vary) → the headers unkeyed
```

## Step 2 — the key-source check — the configured key

```bash
# the proxy's cache-key config
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|hash_data|make_cache_key|Vary' <src> | head -10
#   $uri (without the query) → the params unkeyed
#   $request_uri → the params keyed
#   a hash_data(req.http.X-Forwarded-Host) → that header keyed
```

## Step 3 — the unkeyed-input sweep — the poisoning vector

```bash
# for each candidate input — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Scheme' 'X-Host' 'X-Real-IP' 'X-HTTP-Method-Override'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## Step 4 — the deception-surface check — the privileged page

```bash
# the privileged page — a settings/profile/dashboard
grep -rnoiE 'settings|profile|dashboard|admin|authenticated|session|personalized' <src> | head -10
```

## Step 5 — the poisoning request — the canary

```bash
# send the input → the stored copy carries it
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # stores it
```

## Step 6 — the confirmation — the clean-request read

```bash
# a clean request — a different session, the same URL
curl "$BASE/page?cb=<unique>"   # <marker> reflected? → poisoned
#   the cache-status shows HIT — the stored copy served YOUR input
```

```text
the confirm: the marker persists into the clean response AND the
cache indicator shows the stored copy served it. a reflected marker
on a MISS is not a poisoning.
```

## Step 7 — the deception confirm — the privileged-page serve

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## Step 8 — the TTL measure — the deception's persistence

```bash
# the stored copy's TTL — the Age + the max-age
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'cache-control|age:|expires|max-age'
```

## Step 9 — the blast-radius check — the URL's requester base

```text
a public URL → every visitor (a broad blast)
a cachebuster URL → only your key's requests (a confined blast)
```

## Step 10 — the falsifier — when to move

```text
every candidate input IS keyed → no unkeyed input → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
a reflected marker on a MISS → a reflection, not a poisoning → a
different class.
```

## The per-step ledger — what to record

```bash
python3 tools/state.py <c> --hypothesis \
  "cache-poison-detect-step-<n>: <surface> — input=<unkeyed> — key=<cached-parts>"
```
