# CRLF injection: the header-boundary family

Smuggling-adjacent but distinct: a value you control lands inside a request or
response header *unencoded*, and `\r\n` in it manufactures a second header or a
whole second request. No length ambiguity — the bytes are simply trusted.

## Probe that worked (Weather App)

Put a harmless marker with one folded space character into the interpolated
field and compare the error with an ordinary hostname:

```text
marker-value folded-into-field
```

Expected: the injected bytes appear in the downstream request as their own
header or their own line — the error or reflection shows the split happened.
Falsifier: the marker comes back as a literal inert string, so the field is
encoded before it reaches a header slot.

## The injection alphabet

| Bytes | Effect when unencoded |
|---|---|
| `\r\n` | new header line |
| `\r\n\r\n` | end of headers; rest becomes body/next request |
| folded line (`\r\n ` continuation) | same header visually, different bytes |
| `%0d%0a`, `%0D%0A` | survives one decode layer, splits at the next |
| Unicode lookalikes (`\u010d` etc.) | a lenient decoder normalizes to `\r\n` |

## Where the bytes land

- A URL or hostname field the server interpolates into a request it builds
- A value reflected into a response header (Location, Set-Cookie, custom)
- A filename, callback, or template slot that becomes a header downstream

The exploit path from a bare CRLF: inject a second request line into a
server-built request (smuggling without length tricks), or set a header the
application's own logic then trusts.

## Falsifier

The field is encoded, rejected on `\r\n`, or reflected inert — every byte form
comes back as literal text. Header-boundary injection needs *unencoded*
interpolation; no gap, no class.

## Traps

- A filtered `\r\n` is not the end — folded continuation and one-decode-layer
  encodings often pass where the literal fails.
- A visible `400` on injection is still signal: it proves the bytes reached a
  parser that understood them. Compare the error shape, not just pass/fail.
