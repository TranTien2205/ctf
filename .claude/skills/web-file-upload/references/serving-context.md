# Serving Context — what the serve response headers actually decide

## The read — the fetch response IS the security posture

```
GET /uploads/x.svg →
  Content-Type: image/svg+xml        → renderable → XSS path open
  Content-Type: text/plain           → inert render, but source-visible
  Content-Type: text/html            → runs as HTML — XSS on any markup
  Content-Disposition: attachment    → download — browser-exec dead
  X-Content-Type-Options: nosniff    → no sniff-promotion
  Content-Security-Policy: ...       → script constraints on this response
```

## The four surface types — and what each opens

### 1. `served-raw` (bytes identical, right type)

- `.svg` → stored XSS (if inline-renderable)
- `.html` → stored XSS
- `.php` → source disclosure — flag may live in the source
- `.xml` → in-browser XML render (XSLT angle)
- `.js` → same-origin script available for XSS gadget reuse
- `.txt`/`.json` → info channel only

### 2. `executed-or-transformed` — the server ran something

- `.php` fetched → `uid=33(www)` — PHP exec, done
- `.php` fetched → `Parse error ...` — PHP ran, syntax broke — fix syntax
- `.jpg` fetched → `<?php` absent but payload marker absent too — image
  pipeline rewrote it — not exec
- `x.jsp` fetched → rendered page — JSP exec

### 3. `attachment`/`octet-stream` — download-only

- browser-exec dead for any file
- include/phar/consumer angles still open — `execution-paths.md`
- if `Content-Type: image/svg+xml` + `attachment` — the file won't render
  inline but an `<object>`/`embed`/iframe reference may still load it
  (per-browser, attachment usually still forces download)

### 4. `blocked`/`gone` — not retrievable

- wrong path → `retrieval.md`
- quarantine → `race-and-temp-files.md` timing angles
- different host → check sibling vhosts

## The header-by-header checklist

```
Content-Type:
  + nosniff  → the declared type is forced; no sniff promotion
  + wrong/odd type → sniff-promotion possible if nosniff absent
Content-Disposition:
  inline    → renders
  attachment→ downloads — even for html/svg
X-Content-Type-Options: nosniff → blocks all sniffing
Content-Security-Policy:
  sandbox / default-src 'none' → inert
  script-src 'self'            → inline script dead; external gadgets only
X-Frame-Options / frame-ancestors → iframe embedding allowed?
Access-Control-Allow-Origin: *  → fetch() readable cross-origin (api exfil)
Set-Cookie on this origin       → session cookies in scope for XSS
Cache headers                   → cached = served to other users (stored)
```

## The serve-origin question — cookies and scope

- file on `app.target.com` with session cookies → stored XSS reads them
- file on `static.target.com`/`cdn.target.com` — cookie scope check:
  `Domain=.target.com` cookies still reach `static.target.com`!
- file on `target.s3.amazonaws.com`/`storage.googleapis.com` — foreign
  origin — no cookies; XSS is a defacement/phishing primitive at best
- file on same origin but behind an auth-gated endpoint — bot-view only

## Forced-download defeat — when `attachment` blocks XSS

If the server adds `Content-Disposition: attachment` unconditionally,
inline XSS is dead via direct fetch. The remaining routes:

- `<object>`/iframe embed of the URL — browsers honor `attachment` and
  download instead of rendering — dead too
- app later *includes* the file server-side (`include`/`render`/`import`)
- file is fetched by `fetch()` in the app's JS → response text goes into
  `innerHTML`/eval — the exfil runs through the app's own code
- stored XSS via a SECOND vector: the filename field stored into a page
- `Content-Disposition: attachment; filename="x.svg"` — the disposition
  itself is a header-injection surface on rare parsers

## Sniff-promotion — when `nosniff` is absent

`Content-Type: text/plain` + HTML bytes → browsers may sniff HTML and
render — depends on browser + whether the serving origin allows it. The
payload: plain-text-approved file carrying HTML markup — `m.txt` with
`<script>` may render when fetched directly or embedded.

## The `X-Content-Type-Options` absence check

Fetch the stored file — if `nosniff` is absent, try:

- `.txt` file containing `<script>alert(1)</script>` fetched directly —
  sniff promotion may run it
- embedded `<img src=x.txt>` + sniff → no; `<script src=x.txt>` needs a
  `text/javascript`-ish sniff — Chrome blocks script-src sniffing without
  nosniff anyway for scripts; the HTML-page path is the viable one
- `text/plain` + `<html>` markup in `<iframe src>` — iframe navigation
  renders sniffed HTML

## Output to record

- the verbatim response headers of the stored file's fetch
- which surface type it classifies as
- the origin + cookie scope it lives on
