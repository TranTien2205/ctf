# Worked example: waf-blocked

Reference module for `target-recon`. Recon turns a supplied live
target into the signals classify.py and the routers consume.
Bounded: the supplied port/path only, three commands before any
wordlist, and every observation recorded verbatim.

Walked: probes start 403ing after ~20 requests.

1. cdn-cloudflare identity (cf-ray, cf-cache-status) ->
   rate-based rule tripped (rl-detect: 403 burst shape).
2. Backoff per rl-backoff; enum paused, JS/doc harvest
   continues (low request count, high yield).
3. OPTIONs + neutral paths still work -> enum through what
   the WAF permits (neg-wafblock).
4. Observations: WAF=cloudflare+rate-rule, allowed-method set,
   block threshold ~N/min verbatim.
5. classify on the partial surface; enum resume is a
   decide.py budget question, not recon's call.
## Pivot

Signal harvested -> out-*; route named -> that skill.
