# CDN/WAF identity: cloudflare

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Cloudflare identity: cf-ray header (edge POP
+ ray id), cf-cache-status, cf-request-id, __cf_bm cookie,
server: cloudflare. Predicts: WAF behavior on payloads, edge
caching class (cache-poisoning surface), the real origin
hidden - direct-IP probes may bypass. Origin-finding via
history/cert is a lead, not a claim.
## Pivot

Signal harvested -> out-*; route named -> that skill.
