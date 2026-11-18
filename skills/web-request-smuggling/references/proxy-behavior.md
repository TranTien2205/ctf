# Proxy behavior — which front-end does what

## nginx — the common front

- honors `Content-Length` over `Transfer-Encoding` — CL.TE when back
  honors TE
- strict header-name parsing — rejects `Transfer_Encoding`, spaces
  before colon
- strips `Transfer-Encoding` on some configs — a `proxy_set_header`
  re-emission
- `proxy_http_version 1.1` required for keep-alive + TE — h1.0 default
  ignores TE → falls back to CL
- `proxy_set_header Connection ""` — the keep-alive behavior

## haproxy — the strict parser

- honors `Transfer-Encoding` first — TE.CL when back honors CL
- strict RFC — rejects ambiguous CL/TE
- `option http-buffer-request` — buffers the whole body — desync-less
- `option http-keep-alive` — the shared-socket requirement

## apache httpd — the lenient parser

- honors `Content-Length` — CL.TE when front honors TE
- lenient TE matching — `Transfer_Encoding`, case-fumble, obs-fold
- `mod_proxy` — the `ProxyPass` re-emission
- `SetEnv proxy-nokeepalive` — removes the shared socket

## traefik — the Go-native

- honors `Transfer-Encoding` — TE.CL
- strict header validation — rejects malformed
- `EntryPoints`/`Middlewares` — the route-middleware that may strip
  headers

## envoy — the modern proxy

- strict RFC — rejects CL+TE ambiguous — the desync-resistant front
- `http2` listener — the h2→h1 downgrade
- `header_format` — the header-injection config

## varnish — the caching proxy

- honors `Transfer-Encoding` — TE.CL
- `vcl_recv` — the recv-stage that may strip headers
- the cache layer — `cache-poison-via-smuggle.md`

## cloudfront / cloudflare — the edge proxies

- speak h2 to the client, h1 to the origin — the h2→h1 downgrade —
  `http2-smuggling.md`
- the `content-length`/`transfer-encoding` mistranslation
- the edge-cache — the poison's cache-target

## iis / arr — the Windows front

- honors `Transfer-Encoding` — TE.CL
- lenient TE matching — `Transfer-Encoding : chunked`, obs-fold
- `URL Rewrite` — the `X-Original-URL`/`X-Rewrite-URL` smuggle —
  `header-smuggling.md`

## squid — the forward-proxy

- `CONNECT` tunnel — `tunneling.md`
- the transparent-proxy — intercepts without `CONNECT`

## The pair-table — which pair is live

| Front | Back | Live pair |
|---|---|---|
| nginx | gunicorn/uwsgi | CL.TE or TE.CL |
| nginx | node/express | TE.TE or h2 |
| haproxy | apache | CL.CL or TE.CL |
| haproxy | iis | TE.TE obfuscation |
| traefik | flask/django | header-inheritance |
| envoy | any | h2-downgrade |
| cloudfront | origin | H2.CL / H2.TE |
| varnish | apache | TE.CL |
| iis-arr | asp.net | X-Original-URL |

## The config-grep — the white-box signatures

```bash
grep -rn "proxy_http_version\|proxy_set_header" nginx.conf
grep -rn "option http" haproxy.cfg
grep -rn "ProxyPass\|ProxyPassReverse" httpd.conf
grep -rn "listen.*http2\|listen.*443" *.conf
grep -rn "proxy_cache\|proxy_set_header" nginx.conf
```
