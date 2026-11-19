# Glossary — every CORS term, defined once

## The headers

**Origin** — the request header the browser sets to the page's origin —
`https://evil.com`, `null`, `https://app.t.com`. the CORS gate's input.

**Access-Control-Allow-Origin (ACAO)** — the response header naming which
origin may READ the response — `*` (public), a reflected value, `null`,
or a fixed allowlisted origin.

**Access-Control-Allow-Credentials (ACAC)** — the response header that
permits the credential to ride — `true` or absent. requires a named
ACAO (not `*`).

**Access-Control-Allow-Methods (ACAM)** — the preflight header listing
allowed methods — `GET,POST,...` or `*`.

**Access-Control-Allow-Headers (ACAH)** — the preflight header listing
allowed request headers — the custom-header gate.

**Access-Control-Expose-Headers** — the response headers JS may read —
a token in a non-safelisted header needs to be listed.

**Access-Control-Max-Age** — how long the preflight is cached.

**Access-Control-Request-Method / -Headers** — the preflight request's
method/header ask.

**Vary: Origin** — the cache-key signal — a dynamic ACAO should carry it.

## The request shapes

**simple request** — a GET/HEAD/POST with safelisted headers+content-type —
fires immediately, no preflight. the response's ACAO alone gates the read.

**non-simple request** — a request with a custom header, a non-simple
method, or a non-safelisted content-type — needs an OPTIONS preflight.

**preflight** — the OPTIONS request the browser fires before a non-simple
request — its ACAO/ACAM/ACAH decide whether the real request fires.

**credentialed read** — a fetch with `credentials:'include'` — the
cookie rides AND the response is readable only if ACAO names the
origin AND ACAC:true.

**non-credentialed read** — a fetch without credentials — public data
only; `*` suffices.

**opaque origin** — the `null` origin — a sandboxed iframe, a data:
URL, or a file: page.

## The check shapes

**reflect** — the server echoes the request's Origin — the canonical vuln.

**allowlist** — a fixed list of allowed origins — the closed check.

**prefix/suffix check** — `startswith`/`endswith` on the Origin —
a lookalike bypass.

**substring check** — `'target.com' in origin` — a containing-origin bypass.

**regex check** — a pattern match — a pattern bypass.

**subdomain trust** — `*.target.com` allowed — a controlled-subdomain bypass.

**null allow** — `'null'` in the allowlist — an opaque-origin bypass.

## The related classes

**CSRF** — a cross-origin WRITE — the request fires; CORS is irrelevant
to whether it lands.

**XS-leak** — a cross-origin side-channel measurement — frame-count,
error, timing, cache — not a data read.

**JSONP/XSSI** — a script-tag read — data served AS JavaScript, no CORS.

**postMessage-hijack** — a page that postMessages data to an unverified
origin.

**CSWSH** — a websocket hijack — a ws channel's cookie-auth read+write.

**CORB/CORP/COOP/COEP** — the isolation headers — a resource-load and
window-reference gate layer separate from CORS.

## The actors

**the page** — the foreign-origin JS that makes the read.

**the victim/bot** — the browser whose session cookie rides the fetch.

**the endpoint** — the server route returning the sensitive data.

**the listener** — your exfil endpoint — the OOB readback.

**the allowlist** — the configured set of trusted origins.
