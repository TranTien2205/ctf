# Distributed workers, caching and the measurement hazards

## The load-balancer hazard — the bimodal trap

Behind a balancer, different workers carry different load → response
times split into two bands (fast worker / slow worker). An interleaved
good/bad run that lands on different workers produces a fake timing gap
that is a WORKER effect, not the username.

```bash
# pin both arms to the same worker — a sticky session or a session cookie
curl -sb $cj ...   # same cookie jar -> the balancer pins to one worker
# or a sticky X-Forwarded-For the balancer routes on
```

The fix: session-pinned, interleaved samples; a `b vs b2` spread that
ALSO splits bimodal reveals the worker effect.

## The per-worker counter hazard

A rate-limit/lockout keyed on the worker (not shared) — your requests
hit different workers, each with its own counter → a `429` that fires
inconsistently or at a higher count than expected. The counter is
per-worker, not global — record `counter-scope: per-worker`.

## The caching hazard — a cache busts the oracle

A cached login/response page:
- a `Cache-Control`/`X-Cache: HIT` on the response — the cached body
  does not run the auth logic → NO oracle
- a cached `200`/`404` on `/users/{id}` — the cache serves the
  existence result, still an oracle but a CACHED one
- a cache-buster needed — vary a throwaway param `?_=rand` to bust the
  cache and reach the auth logic

```bash
curl -s -D - -o /dev/null -X POST -d "user=$U&pass=x&_=$RANDOM" "$BASE/login?_=$RANDOM" | grep -i 'x-cache\|cache-control'
```

## The CDN hazard

A CDN-fronted app may:
- cache the auth response → the oracle never reaches the app
- collapse the source-IP → a per-IP counter sees the CDN's IP not yours
- strip/add headers → the counter-key or the oracle-header differs
- a `CF-`/edge header reveals the CDN's own existence/leak

## The distributed-queue send-side

A reset email sent via a queue — the send-latency is variable; a
`{"emails_queued":1}` field is more reliable than the actual send-time.
The send-side oracle is the QUEUE-COUNT field or the actual email, not
the timing.

## The clock-skew hazard

A `Date`/`Retry-After`/`X-RateLimit-Reset` header on a skewed clock —
the window/throttle timing differs from wall-clock; measure the window
empirically (`N per T`) not from the header.

## The affinity-vs-measurement rule

- for TIMING: pin to one worker (same session), interleave, measure
  medians — removes the bimodal worker noise
- for the ORACLE: the worker does not matter — the content/status
  differential is worker-independent
- for the COUNTER: probe whether it is shared or per-worker — a `429`
  that fires at inconsistent counts across requests hints at per-worker

## The distributed verdict record

```
affinity: session-pinned to one worker
cache:    X-Cache: MISS (busted with ?_=rand) — the auth logic ran
counter:  shared global counter (429 at 8 regardless of worker)
```

Record the infrastructure — it explains the measurement, and a per-
worker counter or a cache that busts the oracle is itself a finding.
