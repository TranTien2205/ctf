# Response Header Injection — filename reflected into headers

## The shape — filename lands in a response header

```
Content-Disposition: attachment; filename="YOUR_NAME"
Location: /files/YOUR_NAME
X-Filename: YOUR_NAME
X-Accel-Redirect: /internal/YOUR_NAME
Content-Type: ...; name="YOUR_NAME"
```

If the filename is reflected verbatim, CRLF in it is response-splitting
(`web-request-smuggling`/`web-parser-differential` for HTTP-level detail).

## `filename="..."` injection — the classic

`filename="x";something=` + `filename="x"\r\nSet-Cookie:...` — the
`Content-Disposition` line is a header — CR/LF in the filename escapes it.

Upload name:

```
x.png%0d%0aSet-Cookie:%20pwn=1
```

If the disposition echoes it, the response gains a `Set-Cookie` header —
response-splitting → cache poisoning / cookie injection / XSS via
`Set-Cookie`+`Location` tricks.

## `Location:` redirect injection

If the server responds `Location: /files/<name>`:

- `name` with CRLF → split response → inject body + headers
- `name` starting `javascript:`/`data:` — some clients treat `Location`
  schemes — open redirect or client-side scheme abuse

## `X-Accel-Redirect` / `X-Sendfile` — internal-serve headers

The app signals the front server to serve a file via
`X-Accel-Redirect`/`X-Sendfile`/`X-LIGHTTPD-send-file` — if the filename
influences the value, attacker reads arbitrary internal files:

```
upload "x" → response says X-Accel-Redirect: /internal/<name>
name = ../../etc/passwd → front server serves /etc/passwd
```

This is a file-READ primitive, not exec — but high-value —
`file-read-primitives`/`iis-deep.md`/`nginx-deep.md`.

## `ETag`/`Last-Modified` — secondary reflection

If the filename reaches `ETag`/`Last-Modified`/any header — CRLF is the
same split.

## The URL-encoding question — does the server decode before reflecting?

`filename="x%0d%0a"` — does the server decode `%0d%0a` into real CR/LF
before the header? Test both raw and encoded — some decode one pass,
some none.

## Detection — where the filename echoes

```bash
# after upload:
curl -i "$FILE_URL" | grep -i 'filename\|location\|disposition'
```

Or `http_probe` with `--evidence-regex` on the reflected name:

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-file-upload \
  --url "$FILE_URL" --evidence-regex 'INJECTED_MARKER' \
  --evidence-kind surface --on-match surface --on-miss inconclusive --write-ack
```

A match inside a header line (vs body) = the injection point.

## What CRLF buys beyond XSS

- cache poisoning via injected `Set-Cookie`/`Location`
- cache deception — inject `Cache-Control`+`Content-Type`
- request smuggling-adjacent header splitting — `web-request-smuggling`

## Falsifiers

- filename never reaches any response header
- the reflection sanitizes CR/LF (they arrive as `%0d%0a` literally —
  no split)

## Output to record

- the header line the name landed in + whether real CRLF survived
