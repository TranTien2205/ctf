# Smuggle bypass — the WAF/filter evasions

## The front-end WAF — the path-signature filter

```text
GET /admin HTTP/1.1     — blocked by the front's WAF
```

The WAF runs on the FRONT — the smuggle puts `/admin` inside a chunked
body — the WAF sees only the outer `POST /` — `frontend-bypass.md`.

## The signature-evasion — the payload the WAF never parses

A SQLi/XSS/cmdi payload inside the smuggle's body — the WAF's signature
runs on the OUTER body — the smuggle's payload is opaque to it —
`../web-sqli/`, `../web-xss/`, `../web-command-injection/`.

## The rate-limit bypass — N requests in one

The front counts ONE request — the smuggle is a second request the front
never counted — `frontend-bypass.md`.

## The auth-check bypass — the proxy's auth layer

```text
POST /api/allowed Authorization: Bearer lowpriv
[smuggle: GET /api/admin]
```

The front checks `Authorization` on `/api/allowed` — passes — the smuggle
reaches `/api/admin` unfiltered.

## The path-canonicalization — the `/admin` variants

```text
GET //admin HTTP/1.1
GET /./admin HTTP/1.1
GET /admin/../admin HTTP/1.1
GET /admin%00 HTTP/1.1
GET /admin;.css HTTP/1.1
GET /admin/ HTTP/1.1
GET /ADMIN HTTP/1.1
```

The path-variants — a WAF matching `/admin` exact vs one that normalizes —
`skills/file-read-primitives/references/traversal-variants.md`.

## The header-canonicalization — the `X-Injected` variants

```text
X-Injected: v
X_Injected: v
X_Injected-: v
X-Injected : v
X-Injected:v
```

The header-name variants — a WAF matching `X-Injected` exact vs one that
normalizes — `obfuscation.md`.

## The method-override — `X-HTTP-Method-Override`

```text
POST / HTTP/1.1
X-HTTP-Method-Override: PUT
```

The override — a WAF checking the `POST` method vs the back-end treating
it as `PUT` — `header-smuggling.md`.

## The chunked-body opaque — the WAF can't chunk

A WAF that doesn't de-chunk the body → the smuggle's chunk-data is opaque
— the WAF sees the outer body, not the smuggle — `frontend-bypass.md`.

## The obfuscated-TE — the WAF's TE-parsing

```text
Transfer-Encoding : chunked
Transfer-Encoding: cow
```

The WAF's TE-parsing may differ from the back-end's — a WAF that rejects
`cow` passes the smuggle anyway — `obfuscation.md`.

## The upgrade-tunnel — the WAF's parser-exit

`Upgrade: websocket` — the WAF stops parsing at the tunnel — the smuggle
inside a frame is opaque — `upgrade-smuggling.md`.

## The h2-layer — the WAF's h1-only rules

A WAF with h1-only rules — the h2 request's headers bypass them —
`http2-smuggling.md`.
