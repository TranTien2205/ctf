# Mechanism deep 2 — the internal architecture in detail

## The three-layer stack

```
client (curl/Selenium/Playwright)
    |  HTTP + JSON (W3C WebDriver wire protocol)
    v
driver binary (chromedriver / geckodriver / msedgedriver)
    |  native IPC (DevTools-ish for Chrome, Marionette for Firefox)
    v
browser process (the actual renderer + JS engine + cookie jar)
```

Every WebDriver command traverses all three layers — the client speaks
JSON, the driver translates to the browser's native protocol, the
browser executes and returns through the same path. This is why
WebDriver and CDP are two APIs over the same browser: WebDriver is the
portable standard at the top, CDP is the native protocol at the bottom.

## The serialisation boundary

The HTTP/JSON wire between client and driver is a real boundary —
only JSON-safe values cross it:

| In the browser | Across the wire |
|---|---|
| a DOM element | `{"element-6066-11e4-a52e-4f735466cecf":"<id>"}` — an opaque ref |
| a function | `null` (or an error) |
| `undefined`/`Symbol`/`BigInt` | `null` (or an error) |
| a circular object | a serialisation error |
| a `Promise` | pending (sync) or resolved (async+awaitPromise) |
| a typed array/Buffer | a base64 or array form |
| a `Map`/`Set` | a plain object/array |
| `NaN`/`Infinity` | `null` or a special encoding |

The rule: return JSON-safe values — `el.outerHTML` not `el`, a
primitive or a flat object, and async for promises.

## The frame-context mechanism

`execute`, `source`, `element` all operate on the *current frame* — a
browsing-context pointer that defaults to the top document. `switch_to
.frame` moves the pointer into an iframe; `default_content` returns to
top.

The mechanism is *stronger* than the JS boundary: a cross-origin iframe
is opaque to the top's JS but fully reachable by `switch_to.frame` in
WebDriver — the driver crosses a boundary the page's own JS cannot.
A payload in an iframe is invisible to a top-frame `execute` until you
switch into its frame.

## The element-handle mechanism

`POST /element` returns an opaque id — a *reference* into the browser's
DOM, not the node itself. The id is session-scoped and dies when:

- a navigation replaces the document
- a DOM mutation removes/replaces the node
- the session ends

A stale id on `click`/`text`/`value` returns `stale element reference` —
re-find the element after any mutation.

## The cookie-jar mechanism

`GET /cookies` reads the browser's process-level cookie store — the
jar for the current origin. `document.cookie` reads the *JS view* of
the same jar; `HttpOnly` is a restriction on the JS API, not the store.

The mechanism distinction:
- `GET /cookies` -> the jar — all cookies for the origin, HttpOnly too
- `document.cookie` (via `execute`) -> the JS view — JS-visible only

## The screenshot mechanism

`GET /screenshot` rasterises the current viewport — the compositor's
output, a real render even headless. `--headless=new` rasterises the
full browser; the old `--headless` mode ran a separate code path that
could return blank for some content.

## The session-process mechanism

`POST /session` -> a browser process is spawned (or attached); `DELETE`
-> the process's context is torn down. The session is a lease on the
process:

- one browser per session (not a shared pool)
- a leaked session holds the process open
- on a single-browser driver, a second `POST /session` may fail or
  take the browser over — sessions are serial, not concurrent

## The timeout mechanism

`timeouts` bounds three independent per-command clocks:

- `script` -> `execute/async` max run
- `pageLoad` -> `navigate` max time
- `implicit` -> element-find retry window

Per-command, not a session TTL — a session idle between commands lives
until `DELETE`.

## The attach mechanism

`goog:chromeOptions.debuggerAddress` attaches a session to an already-
running Chrome — reconnects to a live browser's state (cookies, open
pages) rather than spawning a fresh one. The mechanism for driving a
long-lived browser across sessions.
