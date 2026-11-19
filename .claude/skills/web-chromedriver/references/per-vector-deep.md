# Per-vector deep — each channel a flag leaves by, annotated

## The `source` vector

`GET /session/{id}/source` — the rendered DOM as text. The default
read for `file://`, `localhost`, and DOM-resident flags.

- **carries**: the file text in `<pre>`, the rendered tree, hidden fields
- **fails when**: the flag is rendered as an image, or the page errored
- **note**: the *rendered* DOM — not the response body; sanitisation
  and JS have already run

## The `execute` vector

`POST /session/{id}/execute/*` — the JS `return` value. The richest
vector — inherits the browser's origin and cookies.

- **carries**: `document.cookie`, `localStorage`, `fetch` responses,
  computed values
- **fails when**: `execute` is gated; the value is not JSON-serialisable
- **note**: `return el.outerHTML` not `el` (serialisation); async needs
  `awaitPromise`/the callback

## The `cookies` vector

`GET /session/{id}/cookies` — the jar.

- **carries**: `HttpOnly` cookies `document.cookie` cannot see
- **fails when**: the flag is not a cookie, or the jar is filtered
- **note**: jar vs JS-view — the jar is the privileged read

## The `screenshot` vector

`GET /session/{id}/screenshot` — base64 PNG.

- **carries**: a flag rendered visually — an image, a QR, a styled flag
- **fails when**: the flag is text-resident (use `source`), or blank
- **note**: the PNG is the artifact — decode it

## The exfil vector (debugging aid)

The bot's outbound request to your listener — `fetch`, `Image`,
`sendBeacon`, `script`, form, `top.location`.

- **carries**: the flag the payload captured (cookie, DOM, a read)
- **fails when**: egress blocked (CSP/filter/interstitial), or the
  payload never ran
- **note**: the channel is part of the payload — check it from inside

## The write-back vector

The payload writes the flag to a same-origin store you read back.

- **carries**: the flag inside the app's own origin — no egress needed
- **fails when**: no writable same-origin store, or the write fails
- **note**: the app is the channel; your read is a normal request

## The CDP vector

`Runtime.evaluate` + `awaitPromise`, `Network.getResponseBody`,
`Page.captureScreenshot` on `9222`.

- **carries**: response bodies, awaited async results, the render —
  what WebDriver cannot serialise
- **fails when**: `9222` not exposed / no attach
- **note**: the richer read — reach for it when WebDriver cannot

## The vector-selection tree

```
flag is a file?         -> source (file:// nav or execute fetch)
flag is a cookie?       -> jar first (HttpOnly), then JS
flag is storage?        -> execute localStorage
flag is a same-origin?  -> execute fetch
flag is internal route? -> localhost nav + source
flag is rendered?       -> screenshot
flag is bot-exfil'd?    -> exfil or write-back
```

Each vector has a falsifier — a dead vector is a measured state; move
to the next in the tree, do not re-roll the same one.
