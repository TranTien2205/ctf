# Class boundary — CORS vs the confusables

CORS is a READ primitive — the response is the point. The classes
that share its delivery but answer a different question.

---

## 1. CORS vs CSRF — the read/write split

| | CORS | CSRF |
|---|---|---|
| the goal | READ a cross-origin response | fire a WRITE request |
| the gate | ACAO/ACAC on the response | SameSite/token/Origin on the request |
| the request | `cors` mode fetch | `no-cors`/form — no CORS needed |
| reads | yes | never — opaque |

The same fetch mechanics, opposite halves: `cors`+`include` reads;
`no-cors` writes. A CORS-open endpoint can ALSO be CSRF'd — the read
and the write are separate questions.

## 2. CORS vs XSS — the origin question

```text
a CORS-read fetches the data from YOUR origin — weaker than XSS
(which runs JS in the target's origin and reads everything,
including tokens and cookies). if an XSS exists, the CORS read is
subsumed. CORS is the class when NO XSS exists but the endpoint is
still readable cross-origin.
```

## 3. CORS vs XS-leaks — read vs measure

| | CORS | XS-leaks |
|---|---|---|
| what you get | the actual response data | a side-channel bit (frame-count, error, timing, cache) |
| the gate | ACAO/ACAC | none — a measurable side-channel |

An XS-leak reads nothing directly — it infers a difference. CORS
reads the real bytes. When ACAO is closed but a side-channel exists,
`web-xs-leaks` is the class.

## 4. CORS vs SSRF — who fetches

| | CORS | SSRF |
|---|---|---|
| who fetches | the VICTIM's browser | the SERVER |
| the credential | the browser's cookie | the server's network position |

## 5. CORS vs JSONP/XSSI — the script-tag read

```text
a JSONP/XSSI endpoint serves data as JS — readable via <script src>
WITHOUT any ACAO. it's a sibling read primitive — grep for
callback/jsonp or a JS-served endpoint. covered in jsonp-and-
alternates.md.
```

## 6. CORS vs postMessage — a page that broadcasts

```text
a target page that postMessages data to '*' or an unverified origin
— your iframe receives it — a postMessage-hijack read, not CORS.
```

## 7. CORS vs websocket — the ws read

```text
a ws/wss channel with cookie-auth and no Origin check — a read+write
channel — the web-websocket class.
```

## 8. The routing table

```text
a fetch reads a cross-origin response          → web-cors
a write under ambient credentials              → web-csrf
JS in the target's origin                      → web-xss
a script-tag serves the data                   → JSONP/XSSI
an iframe measures a side-channel              → web-xs-leaks
a page postMessages the data                   → postMessage-hijack
a ws channel carries the data                  → web-websocket
the server fetches a URL                       → web-ssrf
```

## 9. The confusable signals — when classify says CORS but it isn't

```text
- 'CORS' in a header but the endpoint is a WRITE → web-csrf
- 'ACAO:*' on a sensitive endpoint → not exploitable — a `*` carries
  no credentials
- a fetch that reads nothing sensitive → no exfil target — not the
  vuln
- a JSONP endpoint → a different read primitive
the classify.py 'web-cors' is a candidate — confirm the READ is
credentialed and sensitive.
```

## 10. The interplay — CORS-read unlocking CSRF-write

```text
a CORS-open /api/csrf-token endpoint returns the token → your page
reads it → uses it in a CSRF-write → the CORS-read breaks the token
defense. the classes chain: a read (CORS) that leaks the capability
a write (CSRF) needs.
```
