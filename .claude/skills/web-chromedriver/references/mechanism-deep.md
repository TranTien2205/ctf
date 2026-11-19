# Mechanism deep — the internals of the command set

## The protocol layering

WebDriver is a thin HTTP layer over the browser's own internals:

```
client --HTTP/JSON--> driver binary --native IPC--> browser process
                          |
                          +-- chromedriver: speaks WebDriver, drives
                              Chrome via DevTools-protocol-ish internals
                          +-- geckodriver: speaks WebDriver, drives
                              Firefox via Marionette
                          +-- msedgedriver: WebDriver -> Edge
```

The driver binary is a translator — your `POST /session/{id}/url`
becomes a DevTools `Page.navigate` inside Chrome. Understanding this
explains why WebDriver and CDP are two APIs over the same browser: one
is the portable standard, the other is the native richer protocol.

## The command dispatch

Every command after `POST /session` is `/{verb} /session/{id}/{command}`:

- `POST /session/{id}/url` -> dispatch to the navigation handler
- `GET /session/{id}/source` -> serialise the current DOM
- `POST /session/{id}/execute/sync` -> run the script, serialise the
  return through the JSON wire protocol

The serialisation matters: `execute` returns JSON-safe values only —
DOM nodes come back as element references, functions/undefined as
null, circular objects as errors. A payload that returns a DOM node
gets `{"element-6066-...": "id"}`, not the node.

## The element-reference mechanism

`POST .../element` returns an opaque element id — a handle into the
browser's DOM, not the node itself. The id is valid only in its
session and goes stale when the DOM changes:

- a navigation invalidates every element id
- a DOM mutation can invalidate the specific node
- a stale id on `click`/`text` returns `stale element reference`

This is why a payload that mutates the DOM between find and click
throws — the handle, not the node, is gone.

## The frame mechanism

`execute`, `source`, `element` all operate on the *current frame* —
the top document unless you `switch_to.frame`. A payload in an iframe
is invisible to a top-frame `execute` — the context boundary is a real
mechanism, not a convenience. The frame tree is:

```
top document
  +-- iframe (separate document, own JS context)
        +-- nested iframe
```

A cross-origin iframe's document is opaque to the top's JS but still
reachable by `switch_to.frame` in WebDriver — the driver crosses the
boundary the JS cannot.

## The cookie-jar mechanism

`GET /session/{id}/cookies` reads the browser's cookie store — a
process-level jar, not the JS `document.cookie` view. This is why it
sees `HttpOnly` cookies: the restriction is on the *JS API*, not the
jar. The mechanism distinction:

- `document.cookie` (via `execute`) -> JS-visible cookies only
- `GET /cookies` -> the jar, all cookies for the current origin

## The screenshot mechanism

`GET /screenshot` rasterises the current viewport — the rendered
pixels, not the DOM. A flag rendered as text is in both `source` and
`screenshot`; a flag rendered as an image/canvas/SVG path may be in
`screenshot` only. The mechanism is a real render — a headless browser
still rasterises.

## The session-process mechanism

`POST /session` spawns (or attaches to) a browser process; `DELETE`
terminates the context. The session is a lease on the process — a
leaked session is a leaked process. On a single-browser driver, a
second `POST /session` may fail or take the browser over — the
mechanism is one browser per session, not a shared pool.

## The timeout mechanism

`timeouts` bounds three independent clocks:

- `script` -> `execute/async` max run time
- `pageLoad` -> `navigate` max time
- `implicit` -> element-find retry window

A `file://` navigation that hangs is bounded by `pageLoad`; a
`fetch` in `execute/async` by `script`. The mechanism is per-command,
not a session TTL — a session without a command lives until `DELETE`.
