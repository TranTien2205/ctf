# Glossary — the cache-poisoning vocabulary

Each term's working definition.

---

## The core terms

**cache poisoning** — YOUR input's effect stored under a URL the
victim requests — the stored copy serves it to every requester.

**cache deception** — a stored response served to the WRONG context
— a privileged page to an anonymous requester, a personalized page
to a public requester.

**cache key** — the set of request parts that determine which stored
copy serves a request — the URL + the Vary'd headers + the configured
key parts.

**unkeyed input** — a request part the app reads but the cache key
ignores — the poisoning vector.

**a stored copy** — the cached response — the evidence a poisoning
requires — a reflected marker on a MISS is a reflection, not a
poisoning.

## The key terms

**Vary** — a response header that names the request headers that
vary the stored entry — a Vary'd header is keyed.

**proxy_cache_key** — an nginx key template — the configured key
parts — the URL + the optional keyed headers.

**cache-buster** — a keyed param the app ignores — the stored entry
is keyed per-value — a keyed param defeats the poisoning.

**a keyed input** — a request part in the cache key — the stored
copy is keyed per-value — not poisonable.

## The status terms

**X-Cache-Status** — an nginx cache-status header — HIT/MISS —
proves the stored copy served the response.

**CF-Cache-Status** — a Cloudflare cache-status header.

**Age** — a cached copy's age — a HIT's indicator.

**a MISS** — the response came from the origin, not the cache — a
reflected marker on a MISS is a reflection.

**a HIT** — the response came from the stored copy — the marker's
reflection came from the cache — the poisoning.

## The vector terms

**an unkeyed header** — a request header the app reflects but the
cache ignores — X-Forwarded-Host, X-Original-URL, Referer, User-Agent.

**an unkeyed param** — a query parameter the app reads but the
cache ignores — a utm, fbclid, gclid.

**an unkeyed cookie** — a cookie the app reads but the cache doesn't
Vary on.

**a path-normalization boundary** — a path the cache and the app
normalize differently — a static-looking URL served the dynamic
response.

## The deception terms

**authenticated-page-served-anonymously** — an authenticated page
cached under a URL the anonymous requester fetches — the stored
copy is the privileged page served to anyone.

**personalized-page-served-publicly** — a personalized page cached
under a shared URL — the stored copy serves YOUR personalized
content to every requester.

**the blast radius** — the URL's requester base — a public URL
poisons every visitor until the entry expires.

**the TTL** — the stored entry's lifetime — the deception's
persistence.

## The class-boundary terms

**a reflection** — a marker reflected on a MISS — the response came
from the origin — not a poisoning.

**a poisoning** — the stored copy serves YOUR input to a different
requester — a HIT's reflected marker.

**a deception** — a stored response served to the wrong context —
a privileged page to an anonymous requester.

**a routing bug** — a path the app routes differently without a
cache — not a cache deception.

## The confirm terms

**the three-part confirm** — the probe stored + the unkeyed input +
the clean-request reflection — all three required.

**the clean-request read** — a different session's request of the
same URL — the marker must reach it.

**the unkeyed-input check** — send the input → check the stored
copy serves it to a clean request — the poisoning vector's test.
