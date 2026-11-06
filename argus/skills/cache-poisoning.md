# Web cache poisoning / deception

**When:** a cache sits in front of the app (CDN, Varnish, nginx proxy_cache,
Cloudflare). Signals: `Age`, `X-Cache`, `CF-RAY`, `Via` headers, static
caching of dynamic-ish pages.

## Unkeyed input -> reflected poison

1. Baseline: GET the page, note a unique marker (`argus<rand>`).
2. Send `X-Forwarded-Host: argus<rand>.com` (or `X-Forwarded-Scheme`,
   `X-Forwarded-For`, `X-Original-URL`, `X-Rewrite-URL`, exotic headers).
3. If the marker echoes in the response AND a second clean request (new
   connection, no header) shows it cached -> poisoned response was stored.
   The clean read-back is the evidence - quote both responses.

Header spray order: `X-Forwarded-Host`, `X-Forwarded-Scheme`,
`X-Original-URL`, `X-Rewrite-URL`, `X-Host`, `X-Forwarded-Server`,
`Fastly-Client-IP`, `Surrogate-Control`, `Cache-Control: no-cache` tricks.

## Cache deception (the inverse)

User-specific page cached under a public-looking key:
`https://app/account/settings` fetched as `.../settings.css` or
`.../settings/` -> stored under a static key -> readable by anyone who
requests that URL. Test: request your profile page with a fake static
suffix from an UNAUTHENTICATED fetch - private data served = deception.

## Key-quest method

Vary ONE header/param at a time while watching `X-Cache: HIT` vs `MISS` and
response diffs; an input that changes the response but NOT the cache key
is your poison channel.

## Falsifier

No response differs under unkeyed inputs, or every differing response is
`MISS`/per-cookie keyed (safe).

## Severity guide

Poisoned page serving attacker content/XSS to all users: high. Private
data via deception: high. Poisoning requiring exotic headers a normal user
can't trigger: medium-low - document the delivery path.
