# Common questions — the CORS confusions, answered once

## Q: a `*` ACAO on /api/me — is that the vuln?

No. `*` means 'any origin may read this NON-CREDENTIALED' — the
browser rejects `*`+credentials. a `*` endpoint reads public data
anyone can fetch. the vuln is a NAMED origin allowed WITH
credentials.

## Q: the ACAO reflects my Origin — am I done?

Half-done. check ACAC — without `ACAC:true` the read carries no
credentials. AND check the cookie's SameSite — a Lax cookie doesn't
attach even with ACAC.

## Q: can I set the `Origin` header myself?

No — `Origin` is browser-set, not JS-controllable. a `curl -H
'Origin: x'` tests the SERVER's check; a real page's Origin is its
context's origin — your domain, or `null` for a sandboxed/data: page.

## Q: a reflected ACAO but the fetch fails in the browser — why?

a `*` + credentials? a SameSite=Lax cookie? a custom header with no
preflight permission? each is a different gate — check all three.

## Q: does CORS block the request or just the read?

Both — a simple request fires and its response is blocked from JS;
a non-simple request's preflight can block the request entirely.
the WRITE always fires (CSRF); the READ is what CORS gates.

## Q: `null` origin — what makes a page's Origin `null`?

a sandboxed iframe (`sandbox` without `allow-same-origin`), a
`data:` URL, or a `file:` page. the exploit rides an opaque origin.

## Q: a strict allowlist — is there any bypass?

test the battery: lookalike origins (subdomain/prefix/suffix),
`null`, URL-parse confusions (`@`,`?`,`#`), encoded dots. a truly
exact-match allowlist has no bypass — pivot.

## Q: the read works but returns 'unauthorized' — why?

the credential didn't ride — a SameSite-gated cookie, or a Bearer
the fetch can't carry. the fetch needs `credentials:'include'` AND
a cookie that attaches.

## Q: JSONP vs CORS — same read?

Different primitives — JSONP serves data AS JavaScript via `<script
src>` with no CORS check; CORS governs the fetch read. both read
cross-origin; the gate differs.

## Q: the preflight is strict — can I still read?

yes — a SIMPLE request (GET or urlencoded POST, no custom headers)
skips the preflight entirely. only the actual response's ACAO
gates it.

## Q: the bot is airgapped — can I still exfil?

the exploit page must live on the target or be a data: URL. the
exfil can be a write-back to the target (a comment you read) or a
page-side readback — not an external fetch.

## Q: `ACAC:true` + `ACAO:*` — the browser rejects it?

yes — `*` never carries credentials. a credentialed read needs a
NAMED origin. `*+ACAC` is an invalid combo.

## Q: how do I know WHICH endpoint to read?

the one carrying the flag — /api/me, /api/flag, /api/admin — grep
the front-end for the authenticated calls. a reflected ACAO on a
public endpoint is noise.

## Q: the response is cached — does that change anything?

a `Vary: Origin` response is per-origin — clean. a shared cache
without Vary may serve a cross-origin response — a cache-poison
surface, and a reason to test with unique origins.

## Q: a websocket read — is that CORS?

no — a ws channel's cookie-auth read is CSWSH — the web-websocket
class. CORS is the fetch-read class.
