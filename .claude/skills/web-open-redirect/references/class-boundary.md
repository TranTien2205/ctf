# Class boundary — what is and is NOT an open redirect

## The class definition

```text
OPEN REDIRECT = the server (or a client-side carrier) emits an
attacker-controlled DESTINATION that the client is sent to. The oracle
is a Location:/meta/JS carrying the canary; the laundered-trust chain
is the value.
```

## The sibling classes — the boundary

| The shape | The class |
|---|---|
| the param lands in a `Location:` | **open-redirect** |
| the param is FETCHED server-side | `web-ssrf` — the fetcher surface |
| the param lands a `javascript:`/`data:` in a DOM-sink | `web-xss` — the DOM-sink twin |
| the `redirect_uri` on an OAuth flow | `web-oauth-sso` — the OAuth twin |
| a `%0d%0a` in the `Location:` | `web-request-smuggling`/header-injection — the CRLF twin |
| a `\@`/`%5c` URL-parser gap on any input | `web-parser-differential` — the general-parser sibling |
| a reflected `?next=` in a link the victim clicks | `web-xss`/`web-info-disclosure` — the phishing surface |
| a `url`/`img` that the server fetches | `web-ssrf` — the fetcher |

## The signal-overlap — the confusable surfaces

```text
the SAME param (a `url`/`next`) can be:
  - an open-redirect surface   (the server 302s to it)
  - an SSRF surface            (the server FETCHES it)
  - an XSS surface             (it's a DOM-sink for a scheme)
  - a phishing surface         (a reflected link)
the distinguishing check: does the RESPONSE carry a `Location:` (open-
redirect) or fetched-CONTENT (SSRF) or a DOM-sink (XSS)?
```

## The open-redirect-vs-SSRF boundary — the fetcher check

```bash
curl -si "$BASE/x?url=https://attacker.invalid"
# response is a 302 + Location: -> open-redirect
# response is a 200 + fetched CONTENT -> SSRF (the server fetched it)
# response is a 200 + the URL reflected -> a reflected-param (XSS/phishing)
```

## The open-redirect-vs-XSS boundary — the scheme check

```text
Location: javascript:alert(1)     <- a javascript: in a Location — most
                                     browsers block a JS-scheme in Location;
                                     it lands on the page's own DOM-sink
                                     which is the XSS twin
location.href = "javascript:..."  <- a DOM-sink -> web-xss
```

## The open-redirect-vs-OAuth boundary — the flow check

```text
/open-redirect?next=evil.com     <- this class — the general redirect param
/oauth/authorize?redirect_uri=   <- web-oauth-sso — the OAuth-flow param
/web-open-redirect               <- the class that LAUNDERS into oauth-sso
```

## The open-redirect-vs-phishing boundary

```text
https://target.com/login?next=https://evil.com  <- a server-side redirect
                                                    the victim lands on
                                                    evil.com — a launder
<a href="https://evil.com">Click here</a>      <- a reflected link — a
                                                    phishing surface —
                                                    NOT a server-side
                                                    open-redirect
```

## The in-class boundary — the surface types

```text
server-side Location:    the canonical open-redirect
client-side meta-refresh: the client-side twin — still this class
client-side JS-nav:       the client-side twin — still this class
stored-redirect:          the two-step — still this class
Referer-derived:          the header-carried — still this class
fragment-carried:         the client-side twin — still this class
```

## The boundary-record

`boundary: <the-param>: <the-response-shape>: <the-class>` — the response
shape names the class; the `Location:` carrying the canary names open-
redirect.
