# Smuggle evidence — the verbatim excerpts

## The confirms — the proving signals

```text
HTTP/1.1 200 OK
Content-Length: 45

flag{the-smuggle-reached-the-internal-route}
```

The smuggle's response body — verbatim — the flag text.

## The second-response — the queue-poison

```text
HTTP/1.1 404 Not Found        — response to YOUR request
HTTP/1.1 200 OK               — a SECOND response — the smuggle's
```

Two responses for one request — `response-poisoning.md`.

## The shifted-response — the next request's response

```text
GET / → HTTP/1.1 200 OK + the smuggle's body
```

The next request's response is the smuggle's — `response-poisoning.md`.

## The injected-header — the fold's echo

```text
HTTP/1.1 200 OK
X-Injected: 1
```

The `X-Injected` header in the response — the fold's echo — `crlf-injection.md`.

## The stored-cookie — the victim's `Cookie:`

```text
x=GET%20/home%20HTTP/1.1%0d%0aCookie:%20session%3DVICTIM%0d%0a
```

The victim's request inside `x=` — `session-hijack.md`.

## The cache-hit — the `X-Cache: HIT`

```text
HTTP/1.1 200 OK
X-Cache: HIT
Age: 120
```

The cache stored the smuggle's response — `cache-poison-via-smuggle.md`.

## The error-body — the parser's rejection

```text
HTTP/1.1 400 Bad Request
invalid chunk size
```

The parser's error — `error-analysis.md`.

## The no-confirm — the negative signals

- `302` — the redirect
- `400` — the parser's rejection
- a single timeout — congestion
- an echo of the input — reflection
- a folded-header echo — proves fold, not smuggle

`evidence-rules.md`.

## The verbatim-excerpt — the `--evidence` requirement

```bash
python3 tools/hooks.py post-probe <name> --request "..." \
  --verdict confirms --evidence-kind class --class web-request-smuggling \
  --hypothesis-id h1 --evidence "HTTP/1.1 404" \
  --response "<the raw response bytes>"
```

`evidence-rules.md`.
