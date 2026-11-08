# HTTP request smuggling / parser differentials

**When:** a front-end (CDN, load balancer, reverse proxy) and back-end
disagree about request boundaries. Signals: proxy headers (`X-Forwarded-*`,
`Via`, `X-Accel`), HTTP/1.1 behind h2 front-end, caching layers.

## Detection - desync primitives

The two classic pairs to compare:

- **CL.TE**: front-end uses Content-Length, back-end uses Transfer-Encoding

```
POST / HTTP/1.1
Content-Length: 13
Transfer-Encoding: chunked

0

G
```

- **TE.CL**: front-end uses TE, back-end uses CL

```
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GPOST / HTTP/1.1
Content-Type: x
Content-Length: 15

x=0
```

Detection signal: a queued SECOND request gets a response for a different
method/route than it sent (404 on a path that exists, or `GPOST` error).
Timing oracles: a smuggled prefix that eats the next request delays it.

## Safe detection first

Send an ambiguous request whose smuggled portion only affects YOUR next
request (queue-poison your own connection). Never aim a smuggled prefix at
a shared queue blindly - other users' requests get captured; that is both
a finding and collateral. One poisoned self-request proves the primitive.

`probe_smuggle` tries canonical CL.TE and TE.CL first, then obfuscated-TE
variants (`xchunked`, trailing-space `chunked `) of CL.TE - the last set
catches a strict front/lenient back pair that a canonical probe misses.

## Transfer-Encoding obfuscations (when plain TE fails)

`Transfer-Encoding: xchunked` · `Transfer-Encoding : chunked` ·
`Transfer-Encoding: chunked ` · `Transfer-Encoding:\tchunked` ·
`Transfer-Encoding: chunked\r\nTransfer-encoding: x` · line-folded headers ·
`Content-Length :` · duplicate/conflicting CL headers

## h2 downgrades

Front-end speaks h2, back-end h1: h2's pseudo-headers can hide a
`transfer-encoding` or extra `content-length` the front-end never sees.
Also: h2 request splitting via `:path`/newline injection.

## Cache-poisoning follow-on

A smuggled request that lands on a cacheable URL poisons the cache for all
users - escalate rating, but verify with a unique canary path only.

## Falsifier

Ambiguous-request set produces consistent self-contained responses with no
cross-request bleed after repeats.

## Severity guide

Request hijack/capture demonstrated: high-critical. Web-cache poisoning via
smuggling: high. Desync affecting only own requests: medium-high (primitive
proven, reachability unclear).
