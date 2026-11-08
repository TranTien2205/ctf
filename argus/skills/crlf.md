# CRLF injection / HTTP response splitting

**When:** a request value lands in a response header without sanitization.
Classic spots: `Location` on redirect endpoints, `Set-Cookie` values,
download filenames (`Content-Disposition`), custom echo headers, error
pages that reflect the path into a header.

## First probes

`probe_crlf <url> <param>` sends two canaries:

- `\r\nX-Argus-Crlf: <random>` - appears as a real response header if the
  parameter is unsanitized (header control).
- `\r\n\r\n<random>` - lands in the body if response splitting works
  (weak signal - reflection alone produces it too).

Manual angle: try `%0d%0aSet-Cookie: argus=1` and read the Set-Cookie
header back, or `%0d%0a%0d%0a<script>alert(1)</script>` for a body split.

## What confirms

- An injected header name/value you control appears verbatim in the
  response headers - quote that header line as evidence.
- Body split: the canary arrives as a NEW body past the real headers -
  confirm the parameter does not reflect normally first.

## Filter bypasses

- `Location` values often get url-encoded EXCEPT the first segment, or
  encoded only for `<>"'` - try `%0d%0a` double-encoded (`%250d%250a`),
  `\r\n` literal, or `%0d%0a` mixed-case.
- Frameworks that fold whitespace: `%09` (tab) before the injected header
  name sometimes slips past naive `key: value` checks.
- Unicode/surrogate tricks: `\u010d\u010a` decoded by the framework AFTER
  the header is assembled.

## Escalation paths

- Injected `Set-Cookie` -> session fixation.
- Injected `Location` -> open redirect even when the endpoint whitelists
  the destination.
- `Content-Length`/`Transfer-Encoding` injection -> cache poisoning or
  desync (load_skill("request-smuggling")).
- Body split -> reflected XSS that bypasses every HTML encoder.

## Falsifier

CRLF canary arrives url-encoded in the header value, or the server
rejects the request with 400 - header assembly is sanitized.

## Severity guide

Header injection (Set-Cookie, Location control): medium. Response
splitting to arbitrary body (stored/cached XSS): high. CRLF inside a
non-header reflection only: informational - it is just reflection.
