# Per-mechanism deep — each primitive's internals

## The navigation primitive

`POST /session/{id}/url` -> the driver translates to a DevTools
`Page.navigate` — the browser loads the URL through its normal loader,
so `file://`, `http://`, `localhost` all work through the same command.

- **reach**: any URL the browser process can resolve
- **read-back**: `source`/`screenshot`/`title` after the load
- **the `pageLoad` bound**: `navigate` returns when the `load` event
  fires (per `pageLoadStrategy`); a never-loading page hangs to the
  `pageLoad` timeout
- **falsifier**: the scheme/host is refused (a `file://` policy block)

## The JS-execution primitive

`POST .../execute/sync` -> `Runtime.evaluate` internally, return value
serialised over the JSON wire.

- **reach**: the page's full JS context — DOM, `fetch`, `localStorage`,
  `document.cookie` — with the browser's origin + cookies
- **serialisation**: JSON-safe values only — elements -> references,
  `undefined`/`function` -> `null`, circular -> error
- **sync vs async**: sync returns the `return` value; async blocks
  until `arguments[last]` is invoked — use async for `fetch` chains
- **falsifier**: a permissions/disabled error

## The cookie-jar primitive

`GET /session/{id}/cookies` -> reads the browser's cookie store for
the current origin — a process-level jar, not the JS view.

- **reach**: all cookies for the origin, `HttpOnly` included
- **the jar-vs-view distinction**: `HttpOnly` restricts `document.cookie`,
  not the jar — the jar read sees what JS cannot
- **falsifier**: empty jar / flag cookie absent for the origin

## The screenshot primitive

`GET .../screenshot` -> the driver rasterises the viewport — a real
render even headless.

- **reach**: whatever the page draws — a flag-as-image, a rendered file
- **the headless note**: `--headless=new` rasterises fully; the old
  `--headless` mode sometimes renders blank — a screenshot falsifier
- **falsifier**: blank/unchanged PNG, or the flag is text-resident

## The frame-switch primitive

`POST .../frame` -> changes the *current frame* `execute`/`source`/
`element` operate on. The boundary the JS cannot cross, the driver can.

- **reach**: any frame's document — cross-origin iframes included
- **the stale-handle note**: a navigation/DOM-mutation invalidates
  element handles — re-find after a switch
- **falsifier**: the target frame is not in the tree

## The reproduction primitive (debugging aid)

A local driver you own, matching the challenge's bot on the behaviour
axes — the observability channel.

- **reach**: console, pageerror, request, requestfailed, DOM, screenshot
- **the fidelity property**: transfers iff flags/wait/cred/url/version
  match live — divergence = a different bot
- **falsifier**: cannot reproduce faithfully (no source, no observation)

## The CDP primitive

`--remote-debugging-port=9222` or `newCDPSession` -> the native protocol.

- **reach**: `Network.*` (bodies), `Runtime.evaluate`+`awaitPromise`,
  `Fetch` interception, `Page.captureScreenshot` — what WebDriver
  cannot serialise
- **falsifier**: `9222` not exposed, or CDP not available

## The primitive-dependency map

```
session -> navigation -> file/loopback reads
        -> execute    -> js/cookie/storage/origin reads
        -> cookies    -> jar read
        -> screenshot -> render read
        -> frame      -> frame-scoped reads
local driver -> reproduction -> observability
9222 -> CDP -> the richer read
```
