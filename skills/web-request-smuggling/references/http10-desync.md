# HTTP/1.0 desync — the no-length boundary

## The shape — h1.0 has no `Transfer-Encoding`

HTTP/1.0 doesn't define chunked encoding or keep-alive by default —
the body boundary is `Content-Length` or the connection-close — a
front-end that upgrades h1.0 to h1.1 re-frames the boundary.

## The no-CL body — the connection-close boundary

```text
POST / HTTP/1.0
Host: t

GET /admin HTTP/1.0
```

No `Content-Length` on h1.0 → the body runs to connection-close →
`GET /admin` is INSIDE the body — a front-end that re-frames to h1.1
splits it — desync.

## The h1.0 keep-alive — `Connection: keep-alive`

```text
POST / HTTP/1.0
Connection: keep-alive
Content-Length: 4

GET /admin HTTP/1.0
```

h1.0 + `keep-alive` — the socket pipelines — a front-end that doesn't
support h1.0 keep-alive → desync.

## The h1.0→h1.1 upgrade — the re-frame

```text
client → h1.0 → front-end → h1.1 → back-end
```

The front-end translates h1.0 to h1.1 — the body's boundary changes —
the connection-close boundary becomes a CL-boundary — the desync.

## The h1.0 `Transfer-Encoding` — the ignored header

```text
POST / HTTP/1.0
Transfer-Encoding: chunked
Content-Length: 4

0

G
```

h1.0 ignores `Transfer-Encoding` — the body is CL-bounded → `0\r\n\r\nG`
is the body → the `G` is inside the body, not a smuggle — but a
front-end that re-frames to h1.1 honors TE → the `G` is a smuggle —
desync.

## The h1.0 `Expect` — the ignored interim

```text
POST / HTTP/1.0
Expect: 100-continue
Content-Length: 100
```

h1.0 ignores `Expect` — the client sends the body without waiting —
a front-end that waits for `100-continue` never gets it → hang —
a version-desync.

## The h1.0 `Host:` — the optional header

```text
POST / HTTP/1.0
```

No `Host:` required on h1.0 — the vhost is the listener — a front-end
that adds `Host:` on the h1.1 re-emit → the back-end routes on the
added Host — a Host-injection.

## The version-downgrade probe — `HTTP/1.0` on an h1.1 socket

```text
POST / HTTP/1.0
Connection: keep-alive
Content-Length: 4

GET /admin HTTP/1.0
```

Forcing h1.0 on an h1.1 connection — the boundary rules change — a
version-desync — `protocol-version.md`.
