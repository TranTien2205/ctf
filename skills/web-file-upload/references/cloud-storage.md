# Cloud Storage — S3/GCS/Azure uploads and presigned-URL abuse

## The shape — the app never touches the bytes

```
browser → GET /api/upload-url → server signs → browser PUTs to S3
browser → GET public URL or CDN URL
```

The server's "upload" is a signing endpoint; validation shifts from
multipart parsing to **policy fields** the client can also touch.

## Where the validation actually lives — presigned POST policy

S3 presigned POST carries a Base64 policy:

```json
{"expiration":"...",
 "conditions":[
   {"bucket":"uploads"},
   ["starts-with","$key","user_uploads/"],
   ["content-length-range",1,1048576],
   {"acl":"private"},
   ["starts-with","$Content-Type","image/"]]}
```

Every condition is attacker-readable — decode the policy from the response
first. Then look for what's MISSING:

| Missing/weak condition | Exploit |
|---|---|
| no `content-length-range` | huge file / zip bomb |
| `starts-with $key "user/"` but no ext | `user/x.php` — any name |
| no `Content-Type` condition | any type — polyglot free |
| `starts-with $key "uploads/"` | key traversal: `uploads/../../x` — S3 keys are literal, but a sibling consumer may decode `..` when serving |
| `{acl: public-read}` or missing + bucket default public | world-readable shell/doc |
| missing `x-amz-meta-*` constraints | metadata injection into downstream processors |
| `success_action_redirect`/`status` | open redirect post-upload |

## Presigned GET/PUT URL abuse

- URL valid for N minutes — replay/steal
- `Content-Type` NOT in the signature → PUT with any type
- `x-amz-server-side-encryption`/`SSE` claims in URL vs headers
- signature covers `key` — no traversal, but the *value* may accept
  `a/b/c` separators and the consumer splits them
- presigned-PUT to `s3://bucket/x` where the app later serves
  `https://cdn/x` — the CDN serves whatever you PUT

## The serve side — `Content-Disposition` and type on read

S3 serves the stored `Content-Type` + whatever `response-content-*` params
the GET URL or the CDN rewrites:

- upload `x.html` with `text/html` — presigned GET serves it inline →
  stored XSS on the bucket domain (and any domain that fronts it without
  a hostname split)
- `?response-content-type=`/`response-content-disposition` on a signed
  GET — if the signing didn't include them... they're *signed* — but a
  non-signed public URL honors them on some buckets
- `X-Content-Type-Options: nosniff` added by CDN → check fetch headers

## Bucket-level check — is the upload even reachable

Uploads to a private bucket are never serveable — the exploit pivot is
the *downstream consumer* (a Lambda/worker that processes the object) —
`second-order-processing.md`.

## GCS / Azure equivalents

- GCS signed URLs — same header-coverage questions; `x-goog-*` fields
- Azure SAS — `sr`/`sp`/`se`/`sig` — the `sp` permission field, `rs*`/
  `response-*` override params (`rscd`, `rsct`, `rsce`, `rscl`, `rsct`)
- Azure `x-ms-blob-content-type` on PUT

## The app's own copy — "fetch then store" servers

`POST /api/upload {url: "https://x"}` — the server fetches your URL into
its bucket: that's SSRF-shaped (→ `web-ssrf` skill) with an upload
consequence — the fetched bytes land in the bucket under a key the server
picks; the attack is what the server fetches, not what you upload.

## Falsifiers

- policy conditions airtight: fixed key prefix + type + length + private
  acl, and no consumer reads the object
- bucket is private with no public/serve path and no downstream worker

## Output to record

- the policy conditions verbatim (decoded)
- the exact missing condition exploited
- the serve URL + served type on fetch-back
