# Transport and concurrency — HTTP/2, batching, and the cheap sweep

## HTTP/2 single-packet-style sweeps

On an HTTP/2 target, many candidate requests share one connection —
the cheapest enum sweep:

```bash
# curl multiplexes h2 on one connection
for u in admin service flag backup deploy; do
  echo "$BASE/api/username-available?u=$u"
done | xargs -P8 -I{} curl -s --http2 {} 
# or a single h2 request batch via nghttp / a client
```

A single connection carries the whole candidate list — no per-request
TCP setup, lower observable footprint than N serial connections.

## GraphQL aliasing — the free batch

```graphql
query{
  a:userExists(username:"admin")
  b:userExists(username:"service")
  c:userExists(username:"flag")
  d:userExists(username:"root")
}
```

One `POST /graphql` sweeps N names — the cheapest possible enum loop;
a per-request throttle counts it as ONE request.

## JSON-array / multi-value batching

```bash
curl -X POST -H 'Content-Type: application/json' -d \
  '{"usernames":["admin","service","flag","root"]}' "$BASE/api/check"
curl -X POST -d 'user=admin,service,flag' "$BASE/check"
curl -X POST -d 'user[]=admin&user[]=service' "$BASE/check"
```

An endpoint accepting a list returns a per-name `exists` map in one
request — a batch oracle, and a throttle-bypass (one request, N names).

## The dup-param / parser-boundary

`user=admin&user=zzz` — which does the app read? First-vs-last-vs-join
is `web-parser-diff`'s question, but the EXISTENCE differential it
produces is still this class's measurement. Record the param-collapse
behavior; route the parser-gap.

## The connection-reuse timing benefit

```bash
# keep-alive reuses the connection -> removes TCP-setup jitter from the timing
curl --keepalive-time 60 -o /dev/null -w '%{time_total}\n' ...
```

Reusing one connection for the interleaved good/bad samples removes
the per-request TCP/TLS setup jitter — tighter timing medians, a more
measurable gap.

## The HEAD/conditional quieter-probe

```bash
curl -sI "$BASE/api/users/$U"            # HEAD — no body
curl -s -H 'If-None-Match: x' "$BASE/..." # a conditional GET
```

A `HEAD`/conditional request returns status without the body — a lower-
footprint existence probe; some counters/loggers weight GET over HEAD.

## The concurrency caution

- parallel requests (`xargs -P`, h2 multiplex) speed the sweep BUT can
  trip a per-IP concurrency throttle faster and inflate the timing
  baseline (contention adds latency)
- measure the timing SERIALLY (interleaved, keep-alive); sweep the
  existence-list in parallel only after the throttle verdict
- a `429` under parallelism is a concurrency-limit, distinct from the
  sequential rate-limit — record which fired

## The transport boundary

- `web-user-enum` — the oracle over whichever transport carries it
- `web-websocket` — a `ws://` auth frame oracle (`{"type":"auth_error",
  "reason":"no_user"}`)
- `web-parser-diff` — a dup-param/multi-value collapse
- `web-host-header` — a host/forwarded-header keyed counter or route
