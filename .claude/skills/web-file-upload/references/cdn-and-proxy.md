# CDN / Proxy Layer — the front that changes the rules

## The shape — the upload goes through a cache/proxy/edge

```
client → CDN/edge → app → storage
       ↓ serves stale/cached/transformed
```

The edge can cache the upload's serve response, transform it, or mangle
the request — creating both bypass and deception paths.

## The "the edge cached my shell" — a `Cache-Control` problem

An uploaded `x.php` whose fetch response carried `Cache-Control:
public, max-age=86400` — the edge caches the RENDERED php output —
the cached copy is the rendered result not the code; the source
stops being served. And the cached response can be poisoned (the
response-splitting variant — `response-header-injection.md`).

## `Accept`/`Content-Type` variants — the Vary-key games

`Vary: Accept`/`Vary: Accept-Encoding` — the edge keys its cache on
those headers — a request `Accept: */*` vs `Accept: image/png` may hit
different cached responses. Upload a payload requesting one variant,
victim's request hits the other.

## The "edge blocks .php" bypass — request smuggling through

`POST /upload` through an edge that strips `.php` from `filename=` —
the origin sees the raw multipart — the edge's filter sees a sanitized
form, the origin parses the raw — the classic CDN-origin disagreement.
Parser-differentials between edge and origin are the whole game.

## Origin-vs-edge extension handling

- edge allows `.jpg` only → sends to origin which stores as `.php`
  (ext rewritten in transit)
- edge normalizes `..%2f` → `../` → the origin sees clean traversal
- edge decompresses `Content-Encoding` → the origin sees inflated size
- edge does `Transfer-Encoding` chunked handling → smuggle boundary
  confusion

## The `X-Forwarded-*` trust — spoofing through the edge

The app trusts `X-Real-IP`/`X-Forwarded-For`/`X-Forwarded-Host` from
the edge — if the edge passes them through, spoofing the real-ip
bypasses IP-based upload limits.

## `ETag`/`If-None-Match` — the revalidation differential

An uploaded file with an `ETag` — `If-None-Match: <etag>` requests get
`304` instead of the content — the 304 path skips the type-check that
the 200 path runs.

## CDN transformation — image CDN re-encoding

A CDN that re-encodes images (`imgproxy`/`thumbor`/cloudflare image
resizing) on the way out — a "polyglot" that survives the origin parse
dies in the CDN's re-encode — the response differs between direct
origin fetch and CDN fetch. The polyglot test needs both paths checked.

## Falsifiers

- no cache/proxy in front — direct origin
- the edge normalizes everything identically to the origin

## Output to record

- which edge header/behavior changes the request before it reaches the
  upload handler
