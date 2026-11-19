# Per-vector — the channels a flag leaves by

## The source vector

`GET /session/{id}/source` — the rendered DOM as text. The default
read for `file://`, `localhost`, and DOM-resident flags. Carries the
file text wrapped in `<html>/<body>`; parse it out.

## The execute vector

`POST /execute/sync` or `/async` — the JS `return` value. Carries:
`document.cookie`, `localStorage`, a `fetch` response, a computed
flag. Richer than `source` for same-origin reads — inherits origin +
cookies.

## The cookies vector

`GET /session/{id}/cookies` — the jar. Carries `HttpOnly` cookies JS
cannot see. The vector of choice when the flag is a cookie the
payload's JS cannot reach.

## The screenshot vector

`GET /session/{id}/screenshot` — base64 PNG. Carries a flag rendered
visually when the text source is mangled or the flag is an image. The
PNG is the artifact.

## The exfil vector (debugging aid)

The bot's outbound request to your listener — `fetch`, `Image`,
`sendBeacon`, `script`, form post, `top.location`. Carries the flag
the payload captured. The vector's liveness is the channel check.

## The same-origin write-back vector

The payload writes the flag to a same-origin store you read — a
profile field, a note, a setting. Carries the flag inside the app's
own origin when off-origin exfil is blocked.

## The CDP vector

`Runtime.evaluate` (with `awaitPromise`), `Network.getResponseBody`,
`Page.captureScreenshot` — the richer read on port `9222`. Carries
bodies WebDriver cannot see and awaited async results.

## The vector-to-flag-location map

| Flag is a | Vector |
|---|---|
| file | source (via `file://` nav or `execute` fetch) |
| JS-visible cookie | execute `document.cookie` |
| HttpOnly cookie | cookies (the jar) |
| localStorage value | execute `localStorage` |
| same-origin page | execute `fetch` or nav + source |
| internal route | nav `localhost` + source |
| rendered image | screenshot |
| exfil'd by payload | exfil (listener) or write-back |

## Choosing the vector

The vector is determined by *where the flag lives*, not preference:

1. a file -> `file://` source
2. a cookie -> jar first (covers HttpOnly), then JS
3. a same-origin resource -> `execute` `fetch`
4. rendered-only -> screenshot
5. off-origin needed -> exfil or write-back

Each vector has its own falsifier — a vector that returns empty or
errors is dead; move to the next in the map, do not re-roll the same
one.
