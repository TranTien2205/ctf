# Content Negotiation — the Accept/Type games on the serve path

## The shape — the same file serves differently per request

`Accept:`/`Accept-Encoding`/`Accept-Charset`/`Accept-Language`/`Range`/
`X-Requested-With` — the same stored file gets different treatment based
on request headers:

- `Accept: text/html` on an `.html` file → rendered
- `Accept: application/octet-stream` → downloaded
- `Range: bytes=0-` → partial content (Range-header quirks)
- `X-Requested-With: XMLHttpRequest` → JSON wrapper vs raw

## `Accept`-based content-type selection — `mod_negotiation`/MultiViews

Apache `MultiViews`: `GET /x` where `x.html`/`x.php`/`x.txt` exist —
picks by `Accept` — `Accept: text/php` might serve `x.php` source vs
execution depending on handler registration.

## The `Range`-request bypass — partial reads skip checks

- `Range: bytes=0-499` — the serving code may skip a type/size check
  that only runs on full reads
- multi-range `bytes=0-0,1-1` — parse quirks per range
- `Range` on a file the handler streams differently — the range path
  reads raw, the full path re-encodes

## `Accept-Charset`/`Accept-Encoding` — encoding games

`Accept-Charset: utf-16`/`Accept-Encoding: gzip` — the served file gets
re-encoded — a type check run pre-encode sees different bytes than the
client gets — the payload survives the check but arrives transformed.

## `X-Requested-With` — the ajax-vs-direct distinction

Some apps serve files differently for XHR vs browser — XHR gets a JSON
wrapper, browser gets raw — the raw path is the XSS/download surface.

## `If-Modified-Since`/`If-None-Match` — 304 vs 200

The 304 path skips the type/content check that runs on the 200 path —
`ETag`/`Last-Modified` from a benign upload, then `If-None-Match` on
the malicious fetch — the 304 path may skip the disposition check.

## The sniffing interplay — `nosniff` + Accept

Without `X-Content-Type-Options: nosniff`, a `Accept: */*` fetch may
sniff HTML out of a `.txt` upload — `file-type-detection-deep.md` — the
Accept header is what lets the browser pick the sniff target.

## The "a different view endpoint" — `?view=`/`?format=`

`?format=raw`/`?view=source`/`?download` — view-mode params change the
serve type — a `?format=raw` on an image serves source; `?format=html`
renders it.

## Detection — test the same URL with different Accept

```bash
curl -H 'Accept: text/html' "$FILE_URL" -o r1
curl -H 'Accept: application/octet-stream' "$FILE_URL" -o r2
diff r1 r2   # different = negotiation in play
```

## Falsifiers

- all Accept variants return identical bytes/type — no negotiation
- `nosniff` + `Content-Disposition: attachment` uniformly enforced

## Output to record

- which request header changes the serve-type + the served-type under
  each
