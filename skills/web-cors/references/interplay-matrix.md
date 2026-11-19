# Interplay matrix — CORS plus the neighbors

How CORS interacts with CSRF, XSS, cache-poisoning, JSONP, and the
alternate-read channels — the decision table for which class the
mechanism is.

---

## 1. CORS + CSRF — the read/write split

| | CORS | CSRF |
|---|---|---|
| the goal | READ the response | fire the WRITE |
| the gate | ACAO+ACAC on the response | SameSite/token/Origin on the request |
| the fetch | `cors`+`credentials:'include'` | `no-cors`/form — opaque |
| the browser | enforces the read | lets the request fire |

A CORS-open endpoint is readable; a CSRF-vulnerable endpoint is
writable. the SAME endpoint can be both — the read leaks the token,
the write uses it.

## 2. CORS + XSS — the same-origin question

```text
an XSS on the target reads /api/me same-origin — CORS is irrelevant.
CORS is the class when NO XSS exists but the endpoint is still
cross-origin readable. a stored XSS subsumes the CORS read.
```

## 3. CORS + cache-poisoning — the Vary interplay

```text
a reflected ACAO WITHOUT Vary: Origin — a shared cache serves the
attacker-origin response to every visitor — a cache-poison+CORS
blend. the cache-poisoning class owns the cache side; the CORS
read is the payload.
```

## 4. CORS + JSONP — the two read primitives

```text
a JSONP endpoint serves data AS JavaScript — a <script src> read
with no CORS check. CORS governs the fetch read. both read the same
data cross-origin — different gates, different pages.
```

## 5. CORS + postMessage — the broadcast vs the fetch

```text
a target page postMessages data to '*' — your iframe receives it —
a postMessage-hijack. a fetch read is the CORS class; a broadcast
read is postMessage-hijack.
```

## 6. CORS + websocket — the ws channel

```text
a ws endpoint with cookie-auth and no Origin check — a CSWSH
read+write — the channel carries the data without CORS. the
web-websocket class.
```

## 7. CORS + SSRF — who fetches

```text
CORS — the victim's BROWSER fetches (its cookie rides).
SSRF — the SERVER fetches (its network position is the privilege).
```

## 8. CORS + XS-leaks — read vs measure

```text
a CORS read gets the actual response bytes. an XS-leak measures a
side-channel (frame-count, error, timing, cache) — no data read.
when ACAO is closed, an XS-leak may still leak a bit — the web-xs-
leaks class.
```

## 9. The interplay decision-table

```text
a fetch reads the response bytes        → web-cors
a no-cors write fires                    → web-csrf
an XSS reads same-origin                 → web-xss (the CORS is moot)
a <script src> serves the data           → JSONP/XSSI
a page postMessages the data             → postMessage-hijack
a ws channel carries the data            → web-websocket
the server fetches a URL                 → web-ssrf
a side-channel measures a difference     → web-xs-leaks
a cached cross-origin response serves    → web-cache-poisoning
```

## 10. The CORS-read unlocks — what a read enables

```text
a read of /api/csrf-token  → a CSRF-write (the token leaked)
a read of /api/flag        → the flag directly
a read of /api/token       → an authenticated-API call
a read of /api/me          → the session's data
a read of a session-token  → a session-hijack replay
```

## 11. The CORS-blocked alternates — when the fetch read is closed

```text
a JSONP endpoint      → the script-tag read
a ws endpoint         → the websocket read
a postMessage page    → the broadcast read
an XSS surface        → the same-origin read
an XS-leak diff       → the side-channel read
a cache-poison        → the stored-leak read
none of the above     → a different bug class
```

## 12. The interplay ledger — the class decision recorded

```bash
python3 tools/state.py <c> --hypothesis \
  "interplay: <mechanism> — class=<chosen> — <why>"
```
