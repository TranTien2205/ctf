# Real-world cases — where desync actually landed

## The `htb-weather-app` chain — the CRLF-into-URL

`knowledge/chains/htb-weather-app-ssrf-crlf-request-smuggling-upsert.json`
— a URL param `host` interpolated raw into `requests.get(f"http://{host}/...")`
— `%0d%0a` folds headers into the outbound request — the upsert through
the smuggle.

## The CL.TE at scale — `nginx → gunicorn`

`nginx` honors `Content-Length`, `gunicorn` honors `Transfer-Encoding` —
the classic CL.TE — the `0\r\n\r\nG` prefix poisons the next request —
PortSwigger's original research.

## The TE.CL at scale — `haproxy → apache`

`haproxy` honors `Transfer-Encoding`, `apache` honors `Content-Length` —
the smuggled full request lands — the internal-route readback.

## The `Transfer-Encoding: chunked` obfuscation — `Transfer-Encoding : chunked`

The space-before-colon — IIS rejects it (invalid header name), nginx
trims it → TE.TE — `obfuscation.md`.

## The duplicate-CL — `CL: 4` / `CL: 7`

`nginx` takes the first, `apache` takes the last → CL.CL — `cl-manipulation.md`.

## The h2→h1 downgrade — `cloudfront → origin`

CloudFront speaks h2, translates to h1 for the origin — the h2
`content-length` header mistranslates → H2.CL — `http2-smuggling.md`.

## The websocket-tunnel — `Upgrade: websocket` + smuggle inside

The ws tunnel proxies raw frames — HTTP inside a frame reaches the
back-end's parser — `upgrade-smuggling.md`.

## The client-side desync — `POST` body ignored

A `POST` route that `302`s without reading the body — the smuggle
poisons the next visitor — `client-side-desync.md`.

## The queue-poison cookie-steal — `POST /steal` + victim's request

The smuggle's `Content-Length` eats the next request — the victim's
`Cookie:` inside the smuggle's body → `session-hijack.md`.

## The cache-poison — the desync → cached response

The smuggle's response caches → every visitor gets the poison —
`cache-poison-via-smuggle.md`.
