# Class boundary — CSRF vs the confusables

CSRF is a DELIVERY primitive — it makes a browser send a request.
The confusables are what the delivery reaches or reads instead.

---

## 1. CSRF vs XSS — the authority question

| | CSRF | XSS |
|---|---|---|
| what the attacker controls | the REQUEST (method, body, URL) | the PAGE's JS context |
| what they can read | nothing — fire-and-forget | the response, the DOM, cookies |
| credential used | ambient cookie/position | JS in the victim's origin |
| needs a delivery vehicle | yes — a page the victim visits | yes — a stored/reflected context |
| token bypass | only if the token is broken | yes — the page's own JS reads the token |

The decision: if you can run JS in the target's origin (XSS exists),
CSRF is subsumed — the XSS does everything CSRF does and reads the
response. CSRF is the class when NO XSS exists but a state change
is still reachable.

## 2. CSRF vs CORS — the read/write split

| | CSRF | CORS-misconfig |
|---|---|---|
| the primitive | WRITE — send a request with credentials | READ — read a cross-origin response |
| the gate | SameSite + token + Origin-check | the ACAO/ACAC response headers |
| the request | doesn't need CORS (no-cors/forms) | needs the response readable (CORS-open) |

A CORS-open endpoint that returns the flag is a READ class (`web-cors`)
— the CSRF skill is for the WRITE. Both can coexist: a CORS-open read
endpoint + a CSRF-able write. The signals differ — CORS needs the
response, CSRF doesn't.

## 3. CSRF vs SSRF — whose server fetches

| | CSRF | SSRF |
|---|---|---|
| who sends | a BROWSER (victim's, bot's) | the SERVER |
| the credential | the browser's cookie/position | the server's network position |
| the gate | SameSite/token/Origin | the URL the server accepts |

The TornadoService card LOOKS like SSRF-adjacent — the bot's browser
reaches 127.0.0.1 — but it's CSRF: the browser, not a server-fetch,
sends it. `web-ssrf` is for `server fetches URL you control`; `web-csrf`
is for `a browser fires a request you shape`.

## 4. CSRF vs XS-leaks — write vs measure

| | CSRF | XS-leaks |
|---|---|---|
| the primitive | change state | MEASURE a cross-origin difference |
| reads | nothing | a side-channel (frame-count, timing, error, cache) |

An XS-leak uses the same cross-origin delivery (a window, an iframe,
a fetch) but to OBSERVE, not write. Different class — `web-xs-leaks`.

## 5. CSRF vs clickjacking — the victim's own action

| | CSRF | clickjacking |
|---|---|---|
| who acts | the attacker's page fires the request | the VICTIM clicks a disguised UI element |
| the gate | SameSite/token/Origin | X-Frame-Options/frame-ancestors |
| needs | a delivery page | a framed target + a user gesture |

Clickjacking needs the target to be FRAMABLE and the victim to
interact. It's not in this taxonomy's card set — CSRF is the class;
a frameable-clickjacking is an adjacent delivery.

## 6. CSRF vs login-CSRF — a CSRF sub-class

```text
login-CSRF is CSRF where the "state change" is a CREDENTIAL SWAP —
the form logs the victim into the attacker's account. same delivery,
different write-semantics. the SSOS card's mechanism.
```

It's inside this skill, not a separate class — the payload-dictionary
carries the login-CSRF shapes.

## 7. CSRF vs stored-content — the delivery location

```text
a CSRF page you HOST on attacker.com delivers cross-site. a page
STORED on the target (a stored-XSS context, a stored-html profile,
a markdown/avatar that renders HTML) delivers SAME-ORIGIN — that
bypasses every cross-origin gate (SameSite, Origin, Referer) and
turns the CSRF into an XSS-adjacent primitive.
```

A stored-HTML field that renders → the "CSRF" page lives on the
target's origin — the form submits same-origin; no SameSite block.
That's the escalation when every cross-origin delivery fails.

## 8. CSRF vs web-host-header / request-smuggling

| | CSRF | host-header/smuggling |
|---|---|---|
| who sends | a browser | an attacker HTTP client |
| the manipulation | the whole request the browser builds | headers/framing the server misreads |

No overlap — different sender, different gate.

## 9. CSRF vs websocket-hijack

```text
a ws/wss connection opened cross-origin carries cookies on the
handshake — 'cross-site websocket hijacking' is CSRF-shaped but
for a ws channel. the message-level auth is in web-websocket.
```

## 10. The routing table

```text
browser sends a request the victim didn't intend      → web-csrf
a page reads a cross-origin response                  → web-cors
a page runs JS in the target's origin                 → web-xss
the server fetches a URL                              → web-ssrf
a page measures a cross-origin side-channel           → web-xs-leaks
a ws channel opened cross-origin                      → web-websocket
a browser write via a stored-on-target page           → stored-CSRF (this skill)
a credential-plant write                              → login-CSRF (this skill)
```

## 11. The confusable signals — when classify says CSRF but it isn't

```text
a classify.py 'web-csrf' candidate is a HYPOTHESIS — the actual
class is decided by the gates:
- if a token the page can't read is required AND enforced → not
  CSRF; the write needs an XSS or a stored page
- if the "write" is actually a read the response carries → CORS
- if the delivery needs the server to fetch → SSRF
the falsifier routes you to the real class.
```
