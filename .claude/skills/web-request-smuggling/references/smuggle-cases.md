# Smuggle cases — the challenge-level shapes

## Case 1 — the `htb-weather-app` — the CRLF-fold

`knowledge/chains/htb-weather-app-ssrf-crlf-request-smuggling-upsert.json` —
a `host` URL-param interpolated raw into `requests.get(f"http://{host}/")` —
`%0d%0a` folds headers into the outbound request — `crlf-injection.md`.

## Case 2 — the classic CL.TE — `nginx → gunicorn`

`nginx` honors CL, `gunicorn` honors TE — `0\r\n\r\nG` hangs — CL.TE —
`cl-te-desync.md`.

## Case 3 — the classic TE.CL — `haproxy → apache`

`haproxy` honors TE, `apache` honors CL — `5c\r\nGET /admin...` — the
smuggle lands — `cl-te-desync.md`.

## Case 4 — the TE.TE — the obfuscated `Transfer-Encoding`

`Transfer-Encoding : chunked` — one parser rejects, one honors —
`obfuscation.md`.

## Case 5 — the CL.CL — the dup-CL

`CL:4 CL:7` — first-wins vs last-wins — `cl-manipulation.md`.

## Case 6 — the CL.0 — the body-ignored route

`POST /redirect` body ignored — `GET /admin` inside — `client-side-desync.md`.

## Case 7 — the h2-downgrade — `content-length:0` inside h2

h2 front, h1 back — `content-length` mistranslates — `http2-smuggling.md`.

## Case 8 — the upgrade-tunnel — `Upgrade: ws` + HTTP inside frame

`upgrade-smuggling.md`.

## Case 9 — the CONNECT — the raw tunnel

`CONNECT internal:80` — `tunneling.md`.

## Case 10 — the cookie-steal — `POST /store` + victim's request

`session-hijack.md`.

## Case 11 — the cache-poison — `GET /?cb=xyz Host: evil.com`

`cache-poison-via-smuggle.md`.

## Case 12 — the internal-route — `GET /flag Host: internal`

`internal-routes.md`.
